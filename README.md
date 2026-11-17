# CueClerk

Your prompt-refinement secretary. **v1.0.0**

CueClerk clarifies vague requests and polishes prompts while preserving your intent. Get the rewritten prompt directly, or choose from **1–4 useful options**
and have the selected task carried out without another confirmation. Each option
has a title and full prompt. Native choices are used when available; long prompts
use text.

An assistant may also use CueClerk when uncertainty about the goal, scope or expected
output would materially affect execution. It helps you confirm the intended task
before proceeding. A short but clear request does not need this extra step.

## Install

Download your platform's ZIP from the [latest release](https://github.com/linhai-skills/cueclerk/releases/latest).
This repository is **private**: sign in with access, or ask the owner to share the ZIP.
No GitHub CLI is required. Extract to a permanent folder before installing a local plugin.

| Platform | Download | Install |
| --- | --- | --- |
| Codex | `cueclerk-codex-1.0.0.zip` | Extract, then run the Codex commands below. |
| Claude Code | `cueclerk-claude-code-1.0.0.zip` | Extract, then run the Claude commands below. |
| DeepSeek Harness | `cueclerk-deepseek-harness-1.0.0.zip` | Extract `cueclerk` into `~/.dsh/skills/` (or `$DSH_HOME/skills/`). |
| WorkBuddy | `cueclerk-workbuddy-1.0.0.zip` | Open **Skills → Add Skill → Upload Skill** and select the ZIP. |

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
No Python runtime or helper scripts are required.

**Skill-only alternative:** extract `cueclerk-1.0.0.zip` into `~/.agents/skills/`
for Codex or `~/.claude/skills/` for Claude Code. Invoke `$cueclerk` or `/cueclerk`.
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
The same platform-neutral rules are maintained in `skills/cueclerk`; platform
copies are synchronized for self-contained installation. Platform differences are
limited to packaging, discovery metadata and installation. Only Codex includes
`agents/openai.yaml`. The root license is added to each release package.

## Use and preferences

Choose an option, type its number, or add edits. Say "Execute my latest prompt"
to skip more refinement. `no compact` disables compaction for the current conversation;
`enable compact` re-enables it. New conversations default to enabled. A switch alone
does not choose a prompt. `cancel` stops the workflow.
Compaction requires an exposed host function; unavailable compaction does not block
execution. Selection widgets and compaction depend on each host's actual capabilities.

Preferences stay in the conversation only. See [SKILL.md](skills/cueclerk/SKILL.md)
for the shared workflow.

Validation covers skill format, package contents and local Codex installation.
Model-conversation tests were not run for v1.0.0. Native compaction and behavior
across clients remain unverified.
[MIT license](LICENSE).
