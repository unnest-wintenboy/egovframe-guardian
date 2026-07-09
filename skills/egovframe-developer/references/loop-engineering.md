# Loop Engineering Playbook

Loop engineering means designing the repeatable control loop that guides an agent, not relying on a single clever prompt. In this plugin, loops must be bounded, evidence-led, and tied to eGovFrame standards.

## Core Loop

Use this loop for multi-step eGovFrame implementation, migration, review/fix, compatibility, and distribution ZIP work:

```text
goal -> evidence -> plan -> act -> observe -> verdict -> repeat or stop
```

Each loop cycle must produce observable evidence:

- files inspected or changed
- official portal/reference pages consulted
- scanner findings or absence of findings
- build/test/route/ZIP inspection output
- unresolved gaps and why they remain

## Non-Negotiable Bounds

- Default maximum: 3 cycles.
- Large migration maximum: 5 cycles.
- Stop after the same failure repeats twice.
- Stop before destructive commands unless the user explicitly confirms the action.
- Stop when official evidence is missing, stale, or contradictory.
- Stop when a human decision is needed for architecture, security, licensing, production data, or upstream compatibility.
- Never turn a simple answer, read-only lookup, or user-paused task into an autonomous loop.

## Maker And Checker Split

Keep authoring and verification separate in time, role, or tool surface:

- Maker: implements the smallest useful change.
- Checker: runs scanner/tests and reviews against this playbook.
- Gate: decides whether to continue, stop, or ask the user.

The same agent may perform these phases only when it switches mode explicitly and records evidence from each phase. For larger work, prefer a subagent reviewer or a separate verification pass.

## Loop Types

### Classification Loop

Use before touching unfamiliar projects.

1. Inspect build files, package paths, resources, mapper locations, and deployment files.
2. Classify the project as classic MVC, Boot REST, MSA, batch, mobile, compatibility/support, or mixed.
3. Load the smallest matching reference.
4. Stop if classification remains ambiguous after two evidence passes.

### Implementation Loop

Use for new features or repairs.

1. Select the target layer: controller/API, service, mapper/repository, config, test, or deployment.
2. Edit one layer boundary at a time.
3. Run the project's relevant test/build surface or the local scanner.
4. Fix only findings caused by the current change.
5. Stop when scanner/build/test evidence is clean or when remaining issues require user policy.

### Review-Fix Loop

Use for code review findings.

1. Group findings into blocker, warning, and advisory.
2. Fix blockers first.
3. Run the narrowest test or scanner that proves the fix.
4. Re-check only the changed surface.
5. Stop when blocker findings are resolved; report warnings separately.

### Distribution ZIP Adoption Loop

Use before applying any eGovFrame portal ZIP.

1. Inspect archive metadata with `scripts/egovframe_distribution.py inspect`.
2. Verify checksum when the portal provides MD5, SHA1, or SHA256.
3. Reject ZIP-slip paths and unexpected executable/script entries unless the user explicitly accepts the risk.
4. Extract only into a temporary or sandbox directory.
5. Apply a curated diff: controller, service, mapper, config, SQL, or deployment files only.
6. Run scanner/tests after adaptation.
7. Stop before copying wholesale archives into the target project.

### Migration Loop

Use when moving classic MVC to Boot, splitting MSA modules, or aligning old code with current standards.

1. Record the existing architecture and version signals.
2. Pick the official reference/sample closest to the target state.
3. Move one vertical slice at a time.
4. Preserve package names, mapper IDs, transaction boundaries, and deployment conventions unless the target standard requires change.
5. Run scanner/tests for each slice.
6. Stop if migration crosses ownership boundaries or needs compatibility certification decisions.

### Source Refresh Loop

Use when portal or GitHub source coverage may be stale.

1. Compare current bundled records with the requested menu, repository, or version.
2. Refresh only the missing area.
3. Rebuild the relevant reference index.
4. Run `scripts/audit_coverage.py`.
5. Stop if upstream pages are unavailable or require manual interpretation.

## Hook Integration

The plugin hooks are loop controls, not decoration:

- `UserPromptSubmit` starts context injection only for eGovFrame-specific prompts.
- `PreToolUse` and `PermissionRequest` are brakes before destructive actions.
- `PostToolUse` is the immediate observe step after edits.
- `Stop` and `SubagentStop` are bounded gates for tracked current-project findings.
- `PostCompact` restores loop context after conversation compression.
- `SubagentStart` passes loop rules only to eGovFrame-relevant subagent work.

Do not add surprise full-project scans to final gates. The loop should be driven by recorded findings and explicit scanner runs.

## Failure Taxonomy

Use these labels when a loop cannot finish:

- `missing-evidence`: required portal/repo/project evidence is absent.
- `stale-source`: bundled source may not match the current upstream release.
- `unsafe-archive`: ZIP inspection found path traversal, checksum mismatch, or risky executables.
- `scanner-blocker`: local guard found high-confidence standard violations.
- `test-failure`: build, unit, integration, route, or batch verification failed.
- `architecture-conflict`: project structure conflicts with the requested target standard.
- `policy-needed`: user or organization must decide suppression, security, compatibility, or licensing policy.

## Completion Contract

A loop is complete only when the final answer can state:

- the goal that was pursued
- the evidence used
- the actions taken
- the verification that passed
- what remains intentionally unresolved

If any of those cannot be named, continue the bounded loop or stop with the correct failure label.
