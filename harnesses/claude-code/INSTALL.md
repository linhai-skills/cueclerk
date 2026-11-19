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

## Verify and update

Update the marketplace files on the machine running Claude Code, then run
`claude plugin update cueclerk@cueclerk-claude` for a plugin install, using the
installed scope. This release remains 1.0.0, so an "already at the latest version"
message alone does not verify updated contents. Reload plugins or start a new
session and inspect the loaded file. If an older client retains a cached copy,
back up that CueClerk copy and reinstall only CueClerk from the updated local
marketplace at the same scope. For a standalone
install, back up the active folder outside skill-discovery paths and replace the
complete folder. Check both project and user installs for an older copy. Start a
new session and verify that the loaded skill includes **Claude Code integration**.

`AskUserQuestion` is used when its current schema accepts the options; one-option
prompts use text if necessary. `/compact` is a user command, unavailable through
the `Skill` tool. This package ships no automatic compaction adapter; without a
separately exposed callable interface, it reports the skip and executes the task.
`no compact` controls CueClerk only, not Claude Code's own automatic compaction.

Validation: packaging and skill format checked; this update has not been tested
in an authenticated Claude Code conversation. To check your client, choose a short
refined task, then verify one execution without a second prompt-selection step.

References: [marketplaces](https://code.claude.com/docs/en/plugin-marketplaces),
[plugin manifest](https://code.claude.com/docs/en/plugins-reference),
[plugin updates](https://code.claude.com/docs/en/plugins/cli-reference#plugin-update),
[skill invocation limits](https://code.claude.com/docs/en/skills#restrict-claudes-skill-access).
