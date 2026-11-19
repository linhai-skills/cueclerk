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

## Verify and update

Import the updated ZIP on each WorkBuddy installation. Preserve any custom copy
before replacing it and keep one enabled CueClerk entry. Check for a project skill
that may load instead, then verify that the active skill includes **WorkBuddy
integration**. File or ZIP presence alone does not prove that the client loaded it.

CueClerk uses an exposed question control when suitable, with numbered text as a
fallback. The reviewed public documentation does not establish an assistant-callable
compaction API. This package supplies no adapter: it checks the current session,
reports a missing callable interface, and continues the accepted task. It leaves
model/context settings unchanged; `no compact` only disables CueClerk's own attempt.

Validation: skill format, ZIP layout and documented import route checked; WorkBuddy
UI import and live execution were not tested here. After import, select a simple
task and check that it executes without repeated prompt confirmation.

Reference: [WorkBuddy skills](https://www.workbuddy.ai/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Skills).
