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

## Verify and update

Back up the active skill outside discovery roots, then replace the complete folder
on the host running the session. Check the skill's reported source: project
`.dsh/skills` and `.agents/skills`, or custom roots, may override the user install.
Reload CueClerk and verify that it includes **DeepSeek Harness integration**.

The native `ask_user_question` control is used when exposed. A timed `pending`
result leaves the choice open; a later answer selects the task without another menu.
The host has a native compaction service and a human `/compact` command, but this
filesystem skill adds no callable service adapter. Without an exposed operation,
CueClerk reports the skip and executes. A queued compaction or a result saying
there is no compactable history is not a completed compaction.

Validation: checked against official source and package layout; no live DeepSeek
Harness conversation was tested. On your client, try a short choice and a free-text
revision, verifying that each accepted task executes once.

References: [skill discovery](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/subsystems/skills.md),
[user questions](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/subsystems/user-questions.md),
[compaction](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/subsystems/compaction.md).
