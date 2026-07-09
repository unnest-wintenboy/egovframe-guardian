# Changelog

## 0.1.1

- Refocus the Korean and English READMEs on everyday user installation and usage.
- Move maintainer CI/CD and release notes into `docs/development.md`.
- Narrow final Stop/SubagentStop gates to tracked findings for the current project root.
- Reduce generic hook false positives and expand Codex/Claude host tool matcher coverage.
- Add Codex hook lifecycle E2E tests.
- Add classic MVC, Boot REST, MSA service, and batch sample scan coverage.
- Pin the public Codex marketplace entry to the `v0.1.1` release tag.

## 0.1.0

- Package the `egovframe-developer` skill inside Codex and Claude Code plugin manifests.
- Add hook-driven eGovFrame guard scanner.
- Add prompt, pre-tool, post-compact, and final Stop lifecycle hooks for stronger local guardrails.
- Add `PermissionRequest`, `SubagentStart`, and `SubagentStop` hooks plus `PLUGIN_DATA` tracked scan state.
- Align hook context with the current eGovFrame portal surface and v5.0.0 highlights.
- Add public Codex and Claude Code marketplace catalogs.
- Add release maturity scoring and public release metadata validation.
- Add pytest guard tests.
- Add CI workflow, release workflow, and distribution metadata.
