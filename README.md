# CueClerk

Your prompt-refinement secretary. **v1.0.0**

CueClerk clarifies vague requests and polishes prompts while preserving your intent. Get the rewritten prompt directly, or choose from **1–4 useful options**
and continue with the selected task without repeating prompt selection, subject to
the host's permission requirements. Each option
has a title and full prompt. Native choices are used when available; long prompts
use text.

An assistant may also use CueClerk when uncertainty about the goal, scope or expected
output would materially affect execution. It helps you confirm the intended task
before proceeding. A short but clear request does not need this extra step.

## Install

Download your platform's ZIP from the [latest release](https://github.com/linhai-skills/cueclerk/releases/latest).
Downloads are public; no GitHub account or repository access is required.
No GitHub CLI is required. Extract to a permanent folder before installing a local plugin.

| Platform | Download | Install |
| --- | --- | --- |
| Codex | `cueclerk-codex-1.0.0.zip` | Extract, then run the Codex commands below. |
| Claude Code | `cueclerk-claude-code-1.0.0.zip` | Extract, then run the Claude commands below. |
| DeepSeek Harness | `cueclerk-deepseek-harness-1.0.0.zip` | Extract `cueclerk` into `~/.dsh/skills/` (or `$DSH_HOME/skills/`). |
| WorkBuddy | `cueclerk-workbuddy-1.0.0.zip` | Open **Skills → Add Skill → Upload Skill** and select the ZIP. |

**Validation scope:** checks cover skill format, packages, local Codex installation
and simulated compaction/continuation events. A live test on a Linux Codex desktop
host with CLI 0.167.0 verified native selection, one completed native compaction
and automatic execution in the same thread, without repeated confirmation or
compaction. Other clients and platforms have not had this live flow verified.
Native selection controls depend on the host.

**Codex automatic compaction:** the Codex package includes an adapter for an existing
App Server Unix control socket. It needs Python 3.10+ on the Codex host and permission
to access that socket. Clients without this interface continue without compaction
unless they expose a native compaction tool. See the [Codex guide](harnesses/codex/INSTALL.md).
Sandbox socket restrictions use the host's normal approval flow first; denied or
unavailable approval falls back to execution without compaction.

**Codex** — replace the path with your extracted folder:

```sh
codex plugin marketplace add /path/to/cueclerk-codex
codex plugin add cueclerk@cueclerk-codex
```

**Claude Code** — run in your terminal:

```sh
claude plugin marketplace add /path/to/cueclerk-claude-code
claude plugin install cueclerk@cueclerk-claude
```

Start a new session. In Claude Code, use `/cueclerk:cueclerk <request>`.
In Codex, select the CueClerk plugin/skill; in DeepSeek Harness or WorkBuddy, ask
"Use CueClerk to refine this request: ...". `~` means your user home directory.
Prompt refinement itself requires no Python. Only the Codex compaction adapter uses it.

**Skill-only alternative:** for Codex, copy the complete `plugin/skills/cueclerk`
folder from `cueclerk-codex-1.0.0.zip` plus `plugin/LICENSE` into
`~/.agents/skills/cueclerk`, then invoke `$cueclerk`. This includes the compaction
adapter. For Claude Code, extract `cueclerk-1.0.0.zip` into `~/.claude/skills/`
and invoke `/cueclerk`. The portable ZIP contains no Codex socket adapter.
Install on each host where you run Codex; updating one machine does not update
another SSH host. Existing `~/.codex/skills/cueclerk` installs can be upgraded
in place using the same complete Codex skill folder.
Use either the plugin or standalone skill to avoid duplicate entries. Back up the
old skill outside discovery directories before replacing it.

## Ask an AI to install

Give your assistant [INSTALL.md](INSTALL.md) and say:
"Install CueClerk for Claude Code using these instructions."
It will use the matching platform guide and report what was actually installed.

## Platform folders

| Folder | Package |
| --- | --- |
| [harnesses/codex](harnesses/codex/INSTALL.md) | Codex plugin manifest, local marketplace and bundled skill |
| [harnesses/claude-code](harnesses/claude-code/INSTALL.md) | Claude plugin manifest, local marketplace and bundled skill |
| [harnesses/deepseek-harness](harnesses/deepseek-harness/INSTALL.md) | Filesystem skill bundle |
| [harnesses/workbuddy](harnesses/workbuddy/INSTALL.md) | Uploadable skill bundle |

The last two use documented skill loading, not an invented plugin manifest.
Platform-neutral rules live in `skills/cueclerk` and are copied to Claude Code,
DeepSeek Harness and WorkBuddy. The Codex skill preserves the shared refinement
workflow and adds its own compaction reference and Python adapter. Keep that
platform-specific section when updating shared rules. The root license is added
to each release package.

## Use and preferences

Choose an option, type its number, or add edits. Say "Skip refinement"
to execute your current request as given. `no compact` disables compaction for the current conversation;
`enable compact` re-enables it. New conversations default to enabled. A switch alone
does not choose a prompt. `cancel` stops the workflow.
Each confirmed task gets at most one automatic compaction attempt. Codex can queue
compaction after the confirming turn ends and continue the task in the same thread.
The continuation skips further compaction and prompt confirmation. Other platforms
use their own callable native interfaces. If none is available, CueClerk reports
that compaction did not occur and continues; a written summary is not compaction.

Preferences stay in the conversation only. The Codex adapter temporarily saves the
confirmed task outside the plugin and keeps a small receipt to prevent duplicates.
See [SKILL.md](skills/cueclerk/SKILL.md) for the shared workflow and
[Codex compaction](harnesses/codex/plugin/skills/cueclerk/references/compaction.md)
for requirements, cancellation and failure handling.

[MIT license](LICENSE).
