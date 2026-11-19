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

Put the introduction and first-use guidance in the native question itself, show
the menu once and map its returned label or ID to the complete prompt. Keep the
choice pending after a default highlight, dismissal, timeout or stale-menu reply.
When a control cannot render the actual option count, use numbered text rather
than padding the menu. A valid answer authorizes the selected prompt immediately.

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

These switches control CueClerk's proactive attempt, leaving the host's independent
automatic context management and global settings unchanged. Before compaction,
retain the selected prompt, amendments, language, current preference and consumed
attempt in conversation context so continuation can execute without reconfirmation.

For each confirmed task, make at most one automatic compaction attempt when enabled,
retaining the accepted prompt, preference and necessary context. Use the current
platform's exposed native compaction interface and report success only after it
completes. If unavailable or unsuccessful, say that compaction did not occur and
continue; if completion is uncertain, say it was not confirmed. A written summary
is context preservation, not native compaction. Other platforms use their own
interfaces, never Codex App Server endpoints.

Check the current host's callable tools and any installed platform adapter before
choosing a fallback. A user-typed slash command or a compaction lifecycle hook
alone does not provide an assistant-callable operation. Report the observed reason
briefly once per task: missing callable interface, missing adapter, denied access,
failure, or unconfirmed completion. Use normal host approval for restricted access;
respect refusal. Resolve an uncertain in-flight operation before resuming execution
so a queued continuation cannot duplicate the task. A confirmed skip consumes this
task's attempt; a new task may check availability again.

Keep the task's compaction-attempt marker through continuation. Continue an accepted
task directly, preserving its amendments and permissions; its continuation consumes
no further compaction attempt and needs no new prompt selection or confirmation.

## WorkBuddy integration

Use the current session's exposed native question control when its schema supports
the complete options; otherwise use numbered text. A skill being enabled or a card
being displayed is not a submitted choice. Keep task selection separate from any
host-required action approval, and continue directly after a valid selection.

This package is an imported skill, with no background worker or compaction adapter.
Check the tools actually available in the current WorkBuddy session. If a permitted
native compaction operation exists, invoke it once and wait for its completion
result before continuing the accepted task. Otherwise say that this session has
no callable compaction interface and execute without proactive compaction. A client
context indicator, automatic context management, or a manually entered command
alone does not establish that CueClerk performed native compaction. Keep the user's
model and context settings unchanged.

Reference: [WorkBuddy skills](https://www.workbuddy.ai/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Skills).
