# Claude Code

Download the platform ZIP from the [latest release](https://github.com/linhai-skills/cueclerk/releases/latest).

This folder is a Claude plugin marketplace. The plugin is in `plugin/`, with a
`.claude-plugin/plugin.json` manifest and `skills/cueclerk`.

Use the absolute path to `harnesses/claude-code` in a checkout, or the permanent
extracted `cueclerk-claude-code` release folder:

```sh
claude plugin marketplace add /path/to/cueclerk-claude-code
claude plugin install cueclerk@cueclerk-claude
claude plugin list
```

Start a new session and invoke `/cueclerk:cueclerk <request>`.
For skill-only installation, copy `plugin/skills/cueclerk` plus the license into
`~/.claude/skills/cueclerk` or `<project>/.claude/skills/cueclerk`; use `/cueclerk`.
Choose one route to avoid duplicate entries. This package does not include Codex UI
metadata or assume an assistant-callable `/compact` operation.

References: [marketplaces](https://code.claude.com/docs/en/plugin-marketplaces),
[plugin manifest](https://code.claude.com/docs/en/plugins-reference).
