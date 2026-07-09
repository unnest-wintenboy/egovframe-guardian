# Development Notes

This document is for maintainers. The root README is written for people installing and using eGovFrame Guardian.

## Local Validation

```bash
python -m json.tool .codex-plugin/plugin.json
python -m json.tool .claude-plugin/plugin.json
python -m json.tool .agents/plugins/marketplace.json
python -m json.tool .claude-plugin/marketplace.json
python scripts/validate_release_package.py .
python scripts/score_maturity.py . --fail-under 130
uv run --with basedpyright basedpyright scripts tests
uv run --with ruff ruff check .
uv run --with pytest pytest
uv run --with pytest --with pytest-cov pytest --cov=egovframe_guard_core --cov=egovframe_guard_hooks --cov=egovframe_guard_state --cov-report=term-missing --cov-fail-under=80
```

If Claude Code is installed:

```bash
claude plugin validate .
```

If Codex plugin creator tooling is installed:

```bash
python ~/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py .
```

## Release Flow

Pull requests and pushes run JSON validation, Python compile checks, strict `basedpyright`, bundled skill validation, reference coverage audit, pytest, coverage, maturity scoring, and public release metadata validation.

Tag releases with semantic version tags:

```bash
git tag vX.Y.Z
git push origin vX.Y.Z
```

The release workflow publishes `.zip` and `.tar.gz` archives, emits SHA-256 checksums, and creates a GitHub Release.

## Publishing Status

This repository publishes a public self-hosted Codex marketplace catalog because official Codex Plugin Directory self-serve publishing is not generally available yet. Claude Code community marketplace submission still requires Anthropic review after local validation.

## Hook Design Notes

The hook policy follows the same practical shape as mature Codex/LazyCodex plugins:

- `SessionStart`, `UserPromptSubmit`, and `PostCompact` provide context.
- `PreToolUse` and `PermissionRequest` block only destructive operations touching eGovFrame or plugin-critical paths.
- Hook matchers include common Codex and Claude Code shell/edit tool names so destructive guards and edit scans are not skipped by host-specific names.
- `PostToolUse` is the primary scanner gate after edits.
- `Stop` and `SubagentStop` do not perform surprise full-project scans. They only block when prior hooks recorded pending work or blocking findings for the current project root.
- `SubagentStart` passes eGovFrame context forward only when the subagent task includes eGovFrame signals.
- `SubagentStop` does not block unrelated subagents unless tracked findings exist.

This keeps guardrails strong after real edits while avoiding noisy end-of-turn blocking for unrelated discussion or read-only exploration.

## Repository Map

```text
README.md                              Korean default README
README.en.md                           English README
.agents/plugins/marketplace.json       Codex marketplace catalog
.codex-plugin/plugin.json              Codex plugin manifest
.claude-plugin/plugin.json             Claude Code plugin manifest
.claude-plugin/marketplace.json        Claude Code marketplace catalog
assets/egovframe-guardian-mascot-retro.png README mascot logo
hooks/hooks.json                       Lifecycle hook configuration
scripts/egovframe_guard.py             Scanner and hook entrypoint
scripts/egovframe_distribution.py      Distribution ZIP inspector
scripts/egovframe_distribution_core.py Distribution inspection logic
skills/egovframe-developer/            Bundled eGovFrame skill and references
tests/                                 Guard and hook tests
```
