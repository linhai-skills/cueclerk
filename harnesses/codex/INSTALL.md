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
Avoid keeping a standalone copy active alongside the plugin. Native choice controls
and compaction are used only when exposed; the package adds neither capability.

Reference: [OpenAI plugin packaging](https://developers.openai.com/plugins/build/plugins).
