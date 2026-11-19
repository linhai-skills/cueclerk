# Codex

Download the platform ZIP from the [latest release](https://github.com/linhai-skills/cueclerk/releases/latest).

This folder is a local plugin marketplace. The plugin is in `plugin/`, with a
`.codex-plugin/plugin.json` manifest and the bundled `skills/cueclerk` skill.

From a source checkout, replace `/path/to/cueclerk-codex` below with the absolute
path to `harnesses/codex`. For the release ZIP, use its extracted folder. Keep it
at a permanent location.

```sh
codex plugin marketplace add /path/to/cueclerk-codex
codex plugin add cueclerk@cueclerk-codex
codex plugin list --marketplace cueclerk-codex --json
```

Start a new session and select CueClerk. If this client has no plugin support,
copy `plugin/skills/cueclerk` plus the license to `~/.agents/skills/cueclerk`
(or `<project>/.agents/skills/cueclerk`) and use `$cueclerk`.
Copy the entire skill folder, including `references/compaction.md`,
`scripts/compact.py` and `scripts/codex_rpc.py`. Avoid keeping a standalone copy
active alongside the plugin.

## Automatic compaction

The adapter uses Python 3.10+ and the existing Codex App Server Unix control socket.
After task confirmation, it saves necessary context, waits for the current turn to
end, requests native compaction, verifies completion, and continues in the same
thread. Each task consumes at most one attempt. Session-level `no compact` and
`enable compact` remain available.

The default socket is under `$CODEX_HOME/app-server-control/` (usually `~/.codex/`).
It must belong to the running host and be accessible under normal host permissions.
When a sandbox blocks the socket, CueClerk requests normal host approval for the
probe and, if available, the handoff operation. A successful read-only probe does
not grant access to later sandboxed commands. Denied approval is respected.
No server or runtime is installed automatically. If the interface is unavailable,
CueClerk reports that compaction did not occur and continues the task. A generated
summary is not treated as native compaction.

Simulated protocol checks and read-only access were verified with Codex CLI 0.167.0;
live model compaction and automatic model continuation have not been tested.
See [compaction requirements and diagnostics](plugin/skills/cueclerk/references/compaction.md).

Reference: [OpenAI plugin packaging](https://developers.openai.com/plugins/build/plugins).
