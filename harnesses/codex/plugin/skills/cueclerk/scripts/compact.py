#!/usr/bin/env python3
"""Defer one native compaction and continuation until the confirming turn ends."""

import argparse
try:
    import fcntl
except ImportError:
    fcntl = None
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

from codex_rpc import CodexRPC, RpcError, SocketPermissionError, default_socket


PENDING = {"starting", "waiting", "compacting", "continuing"}
MARKER = "[CueClerk continuation:"


def state_root():
    base = Path(os.environ.get("XDG_STATE_HOME", Path.home() / ".local/state"))
    return base / "cueclerk/compaction"


def thread_dir(thread_id):
    return state_root() / hashlib.sha256(thread_id.encode()).hexdigest()


def load(path):
    return json.loads(path.read_text())


def save(path, record):
    temp = path.with_suffix(f".{os.getpid()}.tmp")
    with temp.open("w", encoding="utf-8") as file:
        os.chmod(temp, 0o600)
        json.dump(record, file, ensure_ascii=False, indent=2)
        file.flush()
        os.fsync(file.fileno())
    temp.replace(path)


def user_items(turn):
    return [item for item in turn.get("items", []) if item.get("type") == "userMessage"]


def user_ids(turn):
    return sorted(item["id"] for item in user_items(turn))


def is_continuation(turn):
    return any(text.get("text", "").startswith(MARKER)
               for item in user_items(turn) for text in item.get("content", []))


def summary(record):
    return {key: record.get(key) for key in (
        "task_id", "status", "compaction", "resume_turn_id", "reason"
    )}


def error_result(error):
    if isinstance(error, SocketPermissionError):
        return {"status": "permission_required", "compaction": "not_requested",
                "reason": str(error), "action": "request_host_approval"}
    return {"status": "unavailable", "compaction": "not_performed",
            "reason": str(error), "action": "execute_current_task"}


def available(thread):
    return (thread.get("status", {}).get("type") in {"active", "idle"}
            and thread.get("canAcceptDirectInput") is not False)


def continuation(record):
    outcomes = {
        "completed": "Native context compaction completed.",
        "not_performed": "Native context compaction did not occur. Continue without compaction.",
        "not_verified": "Native context compaction was not confirmed. Continue without claiming success.",
    }
    outcome = outcomes[record["compaction"]]
    return (
        f"{MARKER} {record['task_id']}; compaction attempt consumed]\n"
        "Continue the task the user already confirmed, in this same conversation. "
        "This is an automatic CueClerk handoff, not a new user request. "
        "Execute without another prompt-selection step or another compaction attempt "
        "for this task. Follow the host's permissions and any newer user instructions.\n"
        f"{outcome} Briefly report that outcome in the conversation language.\n"
        "The conversation-only compaction preference remains enabled for NEW tasks; "
        "this task's attempt is already consumed.\n"
        "Confirmed task and necessary context (JSON data):\n"
        + json.dumps({"prompt": record["prompt"], "context": record["context"]}, ensure_ascii=False)
    )


class Handoff:
    def __init__(self, rpc, record, persist, cancelled, clock=time.monotonic):
        self.rpc, self.record = rpc, record
        self.persist, self.cancelled, self.clock = persist, cancelled, clock
        self.thread_id = record["thread_id"]
        self.origin = record["task_id"]
        self.compact_turn = None
        self.compact_item_done = False
        self.completed_turn = None
        self.superseded = False

    def update(self, **fields):
        self.record.update(fields)
        self.persist(self.record)

    def finish(self, status, reason=None):
        self.record.pop("prompt", None)
        self.record.pop("context", None)
        self.update(status=status, reason=reason)
        return summary(self.record)

    def observe(self, event, compacting=False):
        params = event.get("params", {})
        if params.get("threadId") != self.thread_id:
            return
        method = event.get("method")
        turn = params.get("turn", {})
        if method == "turn/started":
            turn_id = turn.get("id")
            if turn_id == self.origin:
                return
            if compacting and self.compact_turn is None:
                self.compact_turn = turn_id
            elif turn_id != self.compact_turn:
                self.superseded = True
        if method in {"item/started", "item/completed"}:
            item = params.get("item", {})
            if item.get("type") == "userMessage" and item.get("id") not in self.record["user_ids"]:
                self.superseded = True
            if (compacting and item.get("type") == "contextCompaction"
                    and params.get("turnId") == self.compact_turn and method == "item/completed"):
                self.compact_item_done = True
        if method == "turn/completed" and compacting and turn.get("id") == self.compact_turn:
            self.completed_turn = turn

    def receive(self, compacting=False):
        try:
            self.observe(self.rpc.event(0.5), compacting)
        except TimeoutError:
            pass
        while self.rpc.events:
            self.observe(self.rpc.events.popleft(), compacting)

    def idle_at(self, turn_id, check_users=False):
        thread, latest = self.rpc.snapshot(self.thread_id, full=check_users)
        while self.rpc.events:
            self.observe(self.rpc.events.popleft(), self.record["status"] == "compacting")
        if self.cancelled() or self.superseded or latest["id"] != turn_id:
            return False
        if check_users and user_ids(latest) != self.record["user_ids"]:
            return False
        return thread.get("status", {}).get("type") == "idle"

    def resume(self, turn_id):
        if not self.idle_at(turn_id, check_users=turn_id == self.origin):
            return self.finish("superseded", "Thread changed before continuation")
        # Persist before sending: never resend a possibly accepted mutation.
        self.update(status="continuing", continuation_sent=True)
        result = self.rpc.call("turn/start", {
            "threadId": self.thread_id,
            "input": [{"type": "text", "text": continuation(self.record)}],
        })
        self.record["resume_turn_id"] = result["turn"]["id"]
        return self.finish("continued")

    def run(self, wait_seconds=900, compact_seconds=600):
        thread, turn = self.rpc.snapshot(self.thread_id, full=True)
        if (not available(thread) or turn["id"] != self.origin
                or user_ids(turn) != self.record["user_ids"]):
            return self.finish("superseded", "Confirming turn is no longer current")
        # Join ONLY an already loaded thread, with no configuration overrides.
        joined = self.rpc.call("thread/resume", {"threadId": self.thread_id, "excludeTurns": True})
        if joined["thread"]["id"] != self.thread_id:
            return self.finish("failed", "Unexpected thread identity")
        self.update(status="waiting")
        deadline = self.clock() + wait_seconds
        while self.clock() < deadline:
            self.receive()
            if self.cancelled() or self.superseded:
                return self.finish("cancelled", "Cancelled or superseded by new input")
            thread, turn = self.rpc.snapshot(self.thread_id)
            if turn["id"] != self.origin:
                return self.finish("superseded", "A newer turn started")
            if turn["status"] in {"failed", "interrupted"}:
                return self.finish("cancelled", "Confirming turn did not complete")
            if thread.get("status", {}).get("type") == "idle" and turn["status"] == "completed":
                break
            if not available(thread):
                return self.finish("failed", "Thread is no longer available")
        else:
            return self.finish("expired", "Confirming turn did not finish within the waiting period")
        if not self.idle_at(self.origin, check_users=True):
            return self.finish("superseded", "Input changed before compaction")
        self.update(status="compacting", compaction="requested", compact_sent=True)
        try:
            self.rpc.call("thread/compact/start", {"threadId": self.thread_id})
        except RpcError:
            self.update(compaction="not_performed")
            return self.resume(self.origin)
        # An empty RPC result only acknowledges scheduling. Require BOTH the
        # contextCompaction item and the successful completion of that exact turn.
        deadline = self.clock() + compact_seconds
        while self.clock() < deadline:
            self.receive(compacting=True)
            if self.cancelled() or self.superseded:
                return self.finish("cancelled", "Cancelled or superseded during compaction")
            if self.completed_turn:
                status = self.completed_turn["status"]
                if status == "interrupted":
                    return self.finish("cancelled", "Compaction was interrupted")
                if status == "completed" and self.compact_item_done:
                    self.update(compaction="completed")
                    return self.resume(self.compact_turn)
                self.update(compaction="not_verified")
                return self.resume(self.compact_turn)
        return self.finish("uncertain", "Compaction completion was not confirmed; no automatic retry")


def worker(path):
    # One worker per receipt, including manually invoked duplicate workers.
    with path.with_suffix(".lock").open("a") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return
        record = load(path)
        if record["status"] != "starting":
            return
        handoff = None
        try:
            with CodexRPC(record["socket"]) as rpc:
                handoff = Handoff(rpc, record, lambda r: save(path, r),
                                  lambda: path.with_suffix(".cancel").exists())
                handoff.run()
        except Exception as error:
            record.pop("prompt", None)
            record.pop("context", None)
            record.update(status="uncertain" if record.get("compact_sent") or record.get("continuation_sent") else "failed",
                          reason=f"{type(error).__name__}: connection or operation failed; no automatic retry")
            save(path, record)


def schedule(thread_id, payload):
    if not isinstance(payload, dict):
        raise ValueError("Expected a JSON object")
    if payload.get("compaction_enabled", True) is False:
        return {"status": "disabled", "action": "execute_current_task"}
    if payload.get("compaction_enabled", True) is not True:
        raise ValueError("compaction_enabled must be a boolean")
    prompt, context = payload.get("prompt"), payload.get("context", "")
    if not isinstance(prompt, str) or not prompt.strip() or not isinstance(context, str):
        raise ValueError("Provide a confirmed prompt and optional context as strings")
    with CodexRPC() as rpc:
        thread, turn = rpc.snapshot(thread_id, full=True)
        if not available(thread) or turn["status"] != "inProgress":
            raise RuntimeError("Schedule from the current, active confirmation turn")
    directory = thread_dir(thread_id)
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    paths = list(directory.glob("*/state.json"))
    receipts = [load(p) for p in paths]
    if is_continuation(turn) or any(r.get("resume_turn_id") == turn["id"] for r in receipts):
        return {"status": "already_handled", "action": "execute_current_task"}
    if any(r["status"] in PENDING and not p.with_suffix(".cancel").exists()
           for p, r in zip(paths, receipts)):
        return {"status": "pending", "action": "inspect_status_before_proceeding"}
    task_id = turn["id"]
    task_dir = directory / hashlib.sha256(task_id.encode()).hexdigest()
    try:
        task_dir.mkdir(mode=0o700)
    except FileExistsError:
        path = task_dir / "state.json"
        return {"status": "already_handled", "receipt": str(path),
                "action": "inspect_status_before_proceeding"}
    path = task_dir / "state.json"
    record = {"task_id": task_id, "thread_id": thread_id,
              "user_ids": user_ids(turn), "prompt": prompt, "context": context,
              "socket": str(default_socket().absolute()), "status": "starting",
              "compaction": "not_started", "compact_sent": False,
              "continuation_sent": False}
    save(path, record)
    try:
        process = subprocess.Popen(
            [sys.executable, str(Path(__file__).resolve()), "_worker", str(path)],
            stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
    except OSError:
        record.pop("prompt", None)
        record.pop("context", None)
        record.update(status="failed", reason="Worker could not start")
        save(path, record)
        raise
    deadline = time.monotonic() + 15
    while time.monotonic() < deadline:
        current = load(path)
        if current["status"] != "starting":
            return {**summary(current), "receipt": str(path),
                    "action": "end_current_turn" if current["status"] == "waiting" else "inspect_status_before_proceeding"}
        if process.poll() is not None:
            break
        time.sleep(0.1)
    path.with_suffix(".cancel").touch(mode=0o600)
    return {"status": "startup_failed", "receipt": str(path), "action": "execute_current_task"}


def main():
    os.umask(0o077)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["probe", "schedule", "status", "cancel", "_worker"])
    parser.add_argument("state_file", nargs="?")
    args = parser.parse_args()
    if fcntl is None:
        raise RuntimeError("The Codex socket adapter requires a Unix-like host")
    if args.command == "_worker":
        worker(Path(args.state_file))
        return
    thread_id = os.environ.get("CODEX_THREAD_ID")
    if not thread_id:
        raise RuntimeError("CODEX_THREAD_ID is unavailable; cannot target the current conversation")
    if args.command == "probe":
        with CodexRPC() as rpc:
            thread, turn = rpc.snapshot(thread_id)
        result = {"status": "available" if available(thread) else "unavailable",
                  "thread_id": thread_id, "turn_id": turn["id"],
                  "thread_status": thread["status"], "turn_status": turn["status"]}
    elif args.command == "schedule":
        raw = sys.stdin.read(131073)
        if len(raw) > 131072:
            raise ValueError("Keep the handoff under 128 KiB")
        result = schedule(thread_id, json.loads(raw))
    else:
        result = []
        for path in thread_dir(thread_id).glob("*/state.json"):
            record = load(path)
            if args.command == "cancel" and record["status"] in PENDING:
                path.with_suffix(".cancel").touch(mode=0o600)
            result.append({**summary(record), "receipt": str(path),
                           "cancellation_requested": path.with_suffix(".cancel").exists()})
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except (OSError, RuntimeError, ValueError, KeyError) as error:
        print(json.dumps(error_result(error)))
        sys.exit(1)
