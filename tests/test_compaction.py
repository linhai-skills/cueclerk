"""Protocol/state tests with no model calls or real conversation mutations."""

from collections import deque
import copy
import json
import os
from pathlib import Path
import socket
import struct
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / "harnesses/codex/plugin/skills/cueclerk/scripts"
sys.path.insert(0, str(SCRIPTS))
import compact
from codex_rpc import CodexRPC, RpcError, SocketPermissionError


def event(method, turn_id="compact-turn", thread="thread", **extra):
    params = {"threadId": thread, "turnId": turn_id, **extra}
    if method.startswith("turn/"):
        params["turn"] = {"id": turn_id, "status": "completed" if method.endswith("completed") else "inProgress"}
    return {"method": method, "params": params}


def record():
    return {"thread_id": "thread", "task_id": "confirmed-turn", "user_ids": ["user-1"],
            "status": "starting", "compaction": "not_started", "prompt": "Do the accepted task",
            "context": "Use Chinese", "compact_sent": False, "continuation_sent": False}


class FakeRPC:
    def __init__(self, mode="success"):
        self.events, self.calls = deque(), []
        self.mode = mode
        self.source_completed = False
        self.compacting = False
        self.compacted = False
        self.changed = False

    def __enter__(self):
        return self

    def __exit__(self, *_):
        pass

    def snapshot(self, thread_id, full=False):
        latest = "new-turn" if self.changed else "compact-turn" if self.compacted else "confirmed-turn"
        done = self.source_completed or self.compacted
        status = "completed" if done else "inProgress"
        if self.mode == "source_interrupted" and self.source_completed:
            status = "interrupted"
        return ({"id": thread_id, "status": {"type": "idle" if done else "active"}},
                {"id": latest, "status": status,
                 "items": [{"type": "userMessage", "id": "user-1", "content": []}]})

    def call(self, method, params):
        self.calls.append((method, copy.deepcopy(params)))
        if method == "thread/resume":
            return {"thread": {"id": "thread"}}
        if method == "thread/compact/start":
            assert self.source_completed, "Compaction started during the confirming turn"
            self.compacting = True
            if self.mode == "rpc_rejection":
                raise RpcError(-32601, "Unavailable")
            if self.mode == "lost_reply":
                raise ConnectionError("Reply lost after server might have accepted it")
            self.events.append(event("turn/started"))
            if self.mode == "new_input":
                self.events.append(event("item/started", item={"type": "userMessage", "id": "user-2"}))
            self.events.append(event("item/completed", thread="other", item={"type": "contextCompaction"}))
            if self.mode != "no_item_evidence":
                self.events.append(event("item/completed", item={"type": "contextCompaction"}))
            end = event("turn/completed")
            if self.mode == "compact_interrupted":
                end["params"]["turn"]["status"] = "interrupted"
            self.events.append(end)
            return {}
        if method == "turn/start":
            return {"turn": {"id": "continuation-turn"}}
        raise AssertionError(method)

    def event(self, timeout):
        if not self.compacting:
            self.source_completed = True
            if self.mode == "new_turn_before_compact":
                self.changed = True
            return event("turn/completed", "confirmed-turn")
        self.compacted = True
        result = self.events.popleft()
        if self.mode == "new_turn_before_resume":
            self.changed = True
        return result


class HandoffTests(unittest.TestCase):
    def run_mode(self, mode="success", cancel=False):
        rpc, data, saved = FakeRPC(mode), record(), []
        handoff = compact.Handoff(rpc, data, lambda r: saved.append(copy.deepcopy(r)), lambda: cancel)
        result = handoff.run()
        return rpc, result, saved

    def test_success_waits_then_compacts_once_and_continues_same_thread(self):
        rpc, result, states = self.run_mode()
        self.assertEqual(result["status"], "continued")
        self.assertEqual(result["compaction"], "completed")
        self.assertEqual([m for m, _ in rpc.calls], ["thread/resume", "thread/compact/start", "turn/start"])
        params = rpc.calls[-1][1]
        self.assertEqual(set(params), {"threadId", "input"})  # No permission/model overrides.
        self.assertEqual(params["threadId"], "thread")
        self.assertIn("compaction attempt consumed", params["input"][0]["text"])
        self.assertNotIn("prompt", states[-1])

    def test_rejected_compaction_continues_without_success_claim(self):
        rpc, result, _ = self.run_mode("rpc_rejection")
        self.assertEqual(result["compaction"], "not_performed")
        self.assertIn("did not occur", rpc.calls[-1][1]["input"][0]["text"])

    def test_unrelated_item_event_and_empty_ack_are_not_proof(self):
        rpc, result, _ = self.run_mode("no_item_evidence")
        self.assertEqual(result["compaction"], "not_verified")
        self.assertIn("was not confirmed", rpc.calls[-1][1]["input"][0]["text"])

    def test_stop_and_new_input_do_not_start_stale_task(self):
        for mode in ["source_interrupted", "new_turn_before_compact", "new_input",
                     "compact_interrupted", "new_turn_before_resume"]:
            with self.subTest(mode=mode):
                rpc, result, _ = self.run_mode(mode)
                self.assertNotIn("turn/start", [m for m, _ in rpc.calls])
                self.assertIn(result["status"], {"cancelled", "superseded"})

    def test_cancel_prevents_compaction(self):
        rpc, _, _ = self.run_mode(cancel=True)
        self.assertNotIn("thread/compact/start", [m for m, _ in rpc.calls])

    def test_uncertain_reply_is_never_retried(self):
        rpc = FakeRPC("lost_reply")
        data = record()
        h = compact.Handoff(rpc, data, lambda _: None, lambda: False)
        with self.assertRaises(ConnectionError):
            h.run()
        self.assertTrue(data["compact_sent"])
        self.assertEqual([m for m, _ in rpc.calls].count("thread/compact/start"), 1)
        self.assertNotIn("turn/start", [m for m, _ in rpc.calls])

    def test_disabled_does_not_connect_or_store_preferences(self):
        with patch.object(compact, "CodexRPC") as factory:
            self.assertEqual(compact.schedule("thread", {"compaction_enabled": False})["status"], "disabled")
            factory.assert_not_called()

    def test_socket_permission_is_distinct_and_handoff_is_not_started(self):
        with patch.object(Path, "stat", side_effect=PermissionError("sandbox blocked socket")):
            with self.assertRaises(SocketPermissionError) as caught:
                CodexRPC("/fake/socket")
        self.assertEqual(compact.error_result(caught.exception)["action"], "request_host_approval")
        with patch.object(compact, "CodexRPC", side_effect=caught.exception), \
             patch.object(compact, "save") as persist, \
             patch.object(compact.subprocess, "Popen") as spawn:
            with self.assertRaises(SocketPermissionError):
                compact.schedule("thread", {"prompt": "confirmed task"})
            persist.assert_not_called()
            spawn.assert_not_called()

    def test_missing_socket_and_unrelated_permission_errors_do_not_escalate(self):
        for error in [FileNotFoundError("no socket"), PermissionError("state directory denied"),
                      RpcError(-32000, "operation denied")]:
            with self.subTest(error=type(error).__name__):
                self.assertEqual(compact.error_result(error)["action"], "execute_current_task")

    def test_consumed_receipt_and_continuation_prevent_rescheduling(self):
        with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ, {"XDG_STATE_HOME": directory}):
            task = compact.thread_dir("thread") / compact.hashlib.sha256(b"confirmed-turn").hexdigest()
            task.mkdir(parents=True)
            old = record()
            old.update(status="continued", resume_turn_id="confirmed-turn")
            compact.save(task / "state.json", old)
            with patch.object(compact, "CodexRPC", return_value=FakeRPC()), patch.object(compact.subprocess, "Popen") as spawn:
                self.assertEqual(compact.schedule("thread", {"prompt": "task"})["status"], "already_handled")
                spawn.assert_not_called()
            old.update(status="uncertain", resume_turn_id=None)
            compact.save(task / "state.json", old)
            with patch.object(compact, "CodexRPC", return_value=FakeRPC()), patch.object(compact.subprocess, "Popen") as spawn:
                self.assertEqual(compact.schedule("thread", {"prompt": "task"})["status"], "already_handled")
                spawn.assert_not_called()

    def test_marker_detected_even_without_receipt(self):
        turn = {"items": [{"type": "userMessage", "id": "u", "content": [
            {"type": "text", "text": "[CueClerk continuation: task; compaction attempt consumed]"}]}]}
        self.assertTrue(compact.is_continuation(turn))

    def test_scheduler_waits_for_worker_ready_and_duplicate_is_pending(self):
        with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ, {"XDG_STATE_HOME": directory}):
            launches = []
            def spawn(argv, **kwargs):
                launches.append(kwargs)
                path = Path(argv[-1])
                data = compact.load(path)
                self.assertEqual(data["prompt"], "confirmed")
                data["status"] = "waiting"
                compact.save(path, data)
                return object()  # No polling needed once the worker is ready.
            with patch.object(compact, "CodexRPC", return_value=FakeRPC()), patch.object(compact.subprocess, "Popen", side_effect=spawn):
                first = compact.schedule("thread", {"prompt": "confirmed"})
                second = compact.schedule("thread", {"prompt": "confirmed"})
            self.assertEqual(first["action"], "end_current_turn")
            self.assertEqual(second["status"], "pending")
            self.assertEqual(len(launches), 1)
            self.assertTrue(launches[0]["start_new_session"])
            self.assertEqual(Path(first["receipt"]).stat().st_mode & 0o777, 0o600)

    def test_timeout_never_claims_success_or_starts_continuation(self):
        rpc = FakeRPC()
        data = record()
        h = compact.Handoff(rpc, data, lambda _: None, lambda: False)
        result = h.run(compact_seconds=0)
        self.assertEqual(result["status"], "uncertain")
        self.assertNotIn("turn/start", [m for m, _ in rpc.calls])

    def test_worker_records_unknown_result_and_does_not_retry(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "state.json"
            data = record()
            data["socket"] = "/fake/socket"
            compact.save(path, data)
            rpc = FakeRPC("lost_reply")
            with patch.object(compact, "CodexRPC", return_value=rpc):
                compact.worker(path)
                compact.worker(path)
            saved = compact.load(path)
            self.assertEqual(saved["status"], "uncertain")
            self.assertNotIn("prompt", saved)
            self.assertEqual([m for m, _ in rpc.calls].count("thread/compact/start"), 1)


class TransportTests(unittest.TestCase):
    def setUp(self):
        self.client, self.server = socket.socketpair()
        self.rpc = CodexRPC.__new__(CodexRPC)
        self.rpc.sock, self.rpc.buffer = self.client, bytearray()
        self.rpc.fragments, self.rpc.fragmented = bytearray(), False
        self.rpc.events, self.rpc.sequence, self.rpc.timeout = deque(), 0, 2

    def tearDown(self):
        self.client.close()
        self.server.close()

    def test_fragmentation_ping_and_partial_read_survive_timeout(self):
        self.server.sendall(b'\x01\x05{"hel')
        with self.assertRaises(TimeoutError):
            self.rpc.event(0.01)
        self.server.sendall(b'\x89\x01x' + b'\x80\x06lo":1}')
        self.assertEqual(self.rpc.event(1), {"hello": 1})
        pong = self.server.recv(128)
        self.assertEqual(pong[0] & 15, 10)
        self.assertTrue(pong[1] & 128)

    def test_rpc_retains_notifications_before_response(self):
        notification = json.dumps(event("turn/started")).encode()
        response = b'{"id":1,"result":{}}'
        def frame(data):
            return b'\x81\x7e' + struct.pack('!H', len(data)) + data
        self.server.sendall(frame(notification) + frame(response))
        self.assertEqual(self.rpc.call("thread/compact/start", {"threadId": "thread"}), {})
        self.assertEqual(self.rpc.event()["method"], "turn/started")


if __name__ == "__main__":
    unittest.main()
