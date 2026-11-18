# Native compaction in Codex

Use this workflow only for a task the user has confirmed or explicitly asked to
execute. Refinement-only replies and CueClerk maintenance stay in their existing
workflow. Preserve the conversation language and the latest session-level
`no compact` / `enable compact` preference.

## Choose the available interface

1. For a continuation of an already accepted task, carry its consumed-attempt
   marker forward and execute directly. The `[CueClerk continuation: ...]` marker
   is a handoff receipt, not a new task or an invitation to refine again.
2. When compaction is disabled, execute directly. If a handoff is pending, run
   `scripts/compact.py cancel` first. A standalone switch changes the preference
   without selecting or executing a pending prompt.
3. If the host exposes a permitted native compaction tool, use it once, retain
   the accepted task and preference, verify completion, and continue. An adapter
   attempt is not an additional retry after using that tool.
4. Otherwise use the bundled adapter below. It requires Python 3.10+, a Unix-like
   host, `CODEX_THREAD_ID`, and access to the existing App Server control socket.
   The default socket is `$CODEX_HOME/app-server-control/app-server-control.sock`
   (`CODEX_HOME` defaults to `~/.codex`). `CUECLERK_CODEX_SOCKET` may point to a
   different socket belonging to the same user's running Codex host.

The adapter connects to the existing server. It does not start a second server,
guess another thread, reopen an unloaded thread, change permission policies, or
approve tool requests. Use normal host approval when socket access is restricted.
If that access is unavailable or denied, report that compaction did not occur and
continue the confirmed task using the host's existing permissions. Do not move to
an unrestricted execution path to bypass a denial.

## Queue the handoff

Resolve the script relative to this installed skill, not the project directory.
Run `python3 /absolute/path/to/cueclerk/scripts/compact.py probe` for a read-only
availability check. This checks connectivity and thread state, not model behavior.

Before queuing, preserve the accepted prompt, amendments, conversation language,
deliverable language, relevant file paths, and any necessary facts. Include only
context needed for the task; keep credentials and unrelated conversation out.
Pass a JSON object on stdin, using a quoted heredoc or a tool's structured input:

```sh
python3 /absolute/path/to/cueclerk/scripts/compact.py schedule <<'JSON'
{
  "prompt": "The complete task the user has already confirmed.",
  "context": "Necessary facts, paths, amendments and language requirements.",
  "compaction_enabled": true
}
JSON
```

Use the actual conversation preference. `false` returns `disabled` without
connecting or queuing work. Each confirmation turn gets one durable receipt;
duplicate scheduling and automatic continuation turns cannot queue it again.

- `waiting` / `end_current_turn`: the worker has connected and subscribed. Briefly
  tell the user that compaction is queued and the task will continue afterward,
  then **end the current turn**. Do not execute the task in parallel or wait for
  the worker in a tool call: it is waiting for this turn to end.
- `disabled` or `unavailable`: report that compaction did not occur when relevant,
  and execute in the current turn.
- `pending` or `already_handled`: inspect `status`. Continue only if no worker or
  continuation owns the task; a consumed attempt is never scheduled again.
- `startup_failed` / `failed`: the worker did not queue compaction successfully;
  inspect the receipt, report the failure, and continue without another attempt.

The worker waits up to 15 minutes for the confirming turn to complete successfully.
It then calls `thread/compact/start` once. Its empty response is only an
acknowledgement. Success requires a `contextCompaction` item completion and a
successful `turn/completed` for the same compaction turn. The worker then calls
`turn/start` once on the same thread with the saved task and consumed-attempt marker.
The original thread's model, permissions, and settings are inherited unchanged.

New user input, a newer turn, cancellation, or an interrupted turn cancels the
handoff. A definitive rejection of compaction continues without it. Missing
completion evidence is reported honestly. A disconnect, timeout, or uncertain
mutation result is never retried automatically, to avoid duplicate execution.

## Cancellation and diagnostics

```sh
python3 /absolute/path/to/cueclerk/scripts/compact.py status
python3 /absolute/path/to/cueclerk/scripts/compact.py cancel
```

Both commands apply only to `CODEX_THREAD_ID`. Cancel a pending handoff when the
user stops, disables compaction, or replaces the task. Cancellation prevents future
worker steps; it cannot undo a compaction or continuation already sent. The worker
never interrupts the user's own turn. `enable compact` applies to new tasks and
does not restart a cancelled or consumed attempt.

Receipts live under `$XDG_STATE_HOME/cueclerk/compaction/`, default
`~/.local/state/cueclerk/compaction/`, with private directory/file permissions.
The worker temporarily saves the task there and removes its prompt/context when
it finishes. Minimal receipts remain to prevent duplicates. They are local
handoff state, not preferences shared between conversations, and never belong in
the repository or ZIPs.

If a worker cannot finish, inspect its receipt on the next user interaction.
An `uncertain` result requires checking the thread before continuing manually;
do not report success or blindly resend the mutation. A killed worker can leave
a pending receipt: cancel it before handling later tasks. Do not delete receipts
while their tasks are active.

## Support and validation limits

This adapter targets Codex App Server's Unix WebSocket transport. The protocol and
read-only access were checked against Codex CLI 0.167.0. Ordinary standalone CLI,
Windows, cloud, or desktop sessions without an exposed, accessible control socket
fall back to an actual host tool or continue without compaction. This package does
not make every Codex client expose that capability.

Event handling, duplicate prevention, cancellation and error paths are tested with
simulated RPC. Live model compaction and automatic model continuation have not
been exercised for this implementation. The API has no atomic "start only if the
latest turn is still X" operation: the worker checks for new input before sending,
but a simultaneous user action can still race the final request. Use the latest
user input as authoritative if that happens.

Official protocol: [Codex App Server](https://learn.chatgpt.com/docs/app-server).
