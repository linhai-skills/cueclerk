# Install CueClerk with an AI assistant

Use this file only when the user asks to install CueClerk. Keep installation separate
from the prompt-refinement workflow. Follow the user's chosen platform and scope;
ask only when these cannot be inferred. Do not install into every platform by default.

1. Read the matching platform guide:
   [Codex](harnesses/codex/INSTALL.md),
   [Claude Code](harnesses/claude-code/INSTALL.md),
   [DeepSeek Harness](harnesses/deepseek-harness/INSTALL.md), or
   [WorkBuddy](harnesses/workbuddy/INSTALL.md).
2. Use a local checkout of [linhai-skills/cueclerk](https://github.com/linhai-skills/cueclerk)
   or its [release ZIP](https://github.com/linhai-skills/cueclerk/releases/latest).
   Public downloads require no GitHub account or repository credentials.
3. Inspect existing CueClerk skills/plugins first. Choose one installation route.
   Preserve custom edits. Before replacing an existing skill,
   back it up outside all skill-discovery directories; never delete other skills.
4. Use native plugin installation where documented; otherwise copy the complete
   skill folder or use the host's upload UI. Do not guess a global WorkBuddy path,
   edit unrelated settings, install runtimes, or alter the user's compaction preference.
5. Verify the installed manifest/skill files and native plugin listing where available.
   No Python runtime or helper scripts are needed. Do not invoke the skill merely
   to test installation.
6. Report the destination, method, backup and verification result. Request a new
   session if needed. If a UI step requires user action, name that step without
   claiming it completed. Package validation does not prove live client behavior.

Use normal filesystem operations and host commands; no standalone installer is
required. For source-folder installs, include the root LICENSE in the copied bundle.
The released ZIPs already include it. Preferences apply to the current conversation.

## Maintaining platform copies

Edit the common rules only in `skills/cueclerk`, then copy SKILL.md into every
platform skill folder. Keep host-specific tool names out of these shared rules;
use each host's available capabilities. Copy agents/openai.yaml only
to Codex. Keep manifests and release filenames at the same version. Package actual
files inside each plugin root (no links escaping it), add the root LICENSE and
exclude caches/preferences. Do not restore task state, CI or checksum tooling as
part of ordinary installation.
