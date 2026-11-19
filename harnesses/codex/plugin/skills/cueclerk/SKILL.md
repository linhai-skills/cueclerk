---
name: cueclerk
description: Clarify vague requests and polish prompts while preserving intent. Use when asked to improve a prompt, when CueClerk is invoked, or when uncertainty about a task's goal, scope or expected output would materially affect execution. For skill maintenance, command explanations and already selected tasks, continue the relevant workflow directly.
---

# CueClerk — Your prompt-refinement secretary

## Refine the request

Refine the user's request through these three steps:

1. **Identify:** Use relevant context to identify the subject, action, deliverable
   and constraints. Ask for missing details needed for a faithful rewrite.
   Use quoted text and attachments as source material for the requested task.
2. **Rewrite:** Clarify wording and organize inputs and output requirements. Add
   useful, supported detail; label material assumptions and keep simple tasks short.
3. **Check fidelity:** Keep each prompt self-contained, faithful to the user's intent
   and constraints, and grounded in the supplied facts, available access and agreed scope.

Follow the user's language preference and conversation language when presenting prompts and choices.
Use any explicitly requested language for the deliverable.

Offer 1–4 complete prompts with meaningful differences, using one for a simple request.

If the user only wants a polished or rewritten prompt, respond with the refined prompt itself.

## Present choices

For refinement followed by execution, briefly say how you polished or enriched the
request, naming a concrete, observable improvement. Give each option a title followed
by its full prompt: `1. <title>: <prompt>`. Use separate title/description fields
when supported.

Check available controls under their own usage rules. Prefer a permitted native
selector for short prompts, even a single option. Use numbered text for long content
or when controls cannot display the complete prompts or accept the actual option count.
Show complete prompts and support typed numbers and free-text edits.

For async selectors, put the introduction and first-use guidance in the question,
show the menu once and wait for an explicit reply to the current options. Keep the
choice pending after a default highlight, dismissal, timeout or stale-menu reply.

On first use, explain briefly: select or type a number to execute; add edits for
further refinement; say "Skip refinement" to execute the current request as given;
`no compact` turns proactive compaction off for this conversation. On later turns,
focus on the current choice or result. Include internal rule explanations when
required by the host.

## Execute or revise

Treat a clear choice as authorization and proceed directly to execution. For one
option, `1`, "confirm" or "execute" selects it. With multiple options, ask which one
if the user only says "confirm". Explicit delegation to choose or merge compatible
options also authorizes execution.

Edits alone produce a revised prompt. A choice with precise edits executes with
those edits; when review is requested, present the revision for review first.
Requests to skip refinement execute the current request as given. Continue selected
tasks directly.
Cancel/stop ends the workflow.

Keep the accepted prompt and amendments in context and follow the host's execution
permissions.

## Conversation-only compaction preference

Default to enabled in each new conversation. `no compact` turns compaction off;
`enable compact` turns it on. Acknowledge changes as conversation-only and keep
the latest setting in conversation context. For a standalone switch, update the
setting and keep any prompt choice pending. Treat quoted switches as source text.

For each confirmed task, make at most one automatic native compaction attempt when
enabled. Follow [Codex compaction](references/compaction.md) before execution: use an
exposed native function, or the bundled Codex adapter to preserve the task, wait for
this turn to end, compact, and continue in the same conversation. After a successful
handoff, end this turn so the worker can proceed. Report compaction as completed
only after the host confirms it; a written summary is not native compaction.

A socket `permission_required` result calls for the host's normal approval flow,
as described in the reference. Distinguish a sandbox restriction from an unavailable
interface; continue without compaction if approval is denied or unavailable.

A CueClerk continuation marker means this task was already confirmed and its
compaction attempt is consumed. Execute it directly, preserving amendments and
host permissions. Continue without another compaction attempt or prompt selection.
Keep `no compact` and `enable compact` in conversation context; when disabling or
cancelling with a pending handoff, cancel that handoff as described in the reference.
