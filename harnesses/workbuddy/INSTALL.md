# WorkBuddy

Use WorkBuddy's skill-package import. No undocumented global directory or plugin
manifest is required. The package omits Codex-only UI metadata.

1. Download `cueclerk-workbuddy-1.0.0.zip` from the [latest release](https://github.com/linhai-skills/cueclerk/releases/latest).
2. Open **Skills → Add Skill → Upload Skill**, select the ZIP and finish import.
3. Enable CueClerk and ask it to refine a request in a new conversation.

When preparing a ZIP from source, include this folder's `cueclerk/` directory and
copy the repository's root LICENSE into it. Do not ZIP the entire repository.
If the assistant cannot operate the UI, provide the ZIP and identify the remaining
import step. Verify that CueClerk appears in the enabled skills list before claiming
installation. Native selection and compaction depend on the capabilities exposed by the host.

Reference: [WorkBuddy skills](https://www.workbuddy.ai/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Skills).
