# DeepSeek Harness

Download the platform ZIP from the [latest release](https://github.com/linhai-skills/cueclerk/releases/latest).

Use the documented filesystem skill provider. This is a skill bundle, not a service
provider plugin, and it does not need a plugin manifest or Codex UI metadata.

1. Copy the entire `cueclerk` folder into `$DSH_HOME/skills/`, default
   `~/.dsh/skills/`. For a project-only install, use `<project>/.dsh/skills/`.
2. From source, include the repository's root LICENSE; release ZIPs include it.
3. Start a new session and ask: "Use CueClerk to refine this request: ...".

Confirm that `<destination>/cueclerk/SKILL.md` exists. No helper script is needed.
Respect any custom skill roots configured by the user. A directory copy verifies
installation layout, not model behavior. Native selection/compaction is conditional
on the tools the host exposes.

Reference: [DeepSeek Harness skill discovery](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/subsystems/skills.md).
