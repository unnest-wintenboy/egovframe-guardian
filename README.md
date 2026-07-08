# eGovFrame Guardian

eGovFrame Guardian is a dual-surface plugin for **Codex** and **Claude Code** that helps agents build, review, and maintain applications aligned with the Korean eGovFrame standard framework.

It bundles official eGovFrame portal research, repository indexes, reusable implementation examples, and local guardrail hooks for common eGovFrame project mistakes.

## What It Provides

- `egovframe-developer` skill for eGovFrame classic MVC, eGovFrame Boot REST, MyBatis, security, batch, MSA, compatibility checks, and source refresh workflows.
- Portal-aligned reference bundle covering framework overview, development guide, downloads, developer participation, technical support, compatibility confirmation, and current v5.0.0 highlights.
- Example code for classic MVC CRUD, Boot REST CRUD, security login, batch jobs, MSA service structure, and React client integration.
- Hook-driven scanner for controller SQL leakage, missing MyBatis namespaces, literal secrets, missing transaction boundaries, mapper discovery gaps, and missing eGovFrame runtime metadata.
- CI/CD release automation for validation, packaging, checksums, and GitHub Releases.

## Install In Codex

Add this repository as a Codex plugin marketplace:

```bash
codex plugin marketplace add unnest-wintenboy/egovframe-guardian
```

Then open the Codex plugin directory, choose **eGovFrame Guardian**, install it, review the bundled hook definitions, and enable the plugin.

The repo-scoped Codex marketplace catalog lives at:

```text
.agents/plugins/marketplace.json
```

The plugin itself lives at the repository root and is described by:

```text
.codex-plugin/plugin.json
```

## Install In Claude Code

Add this repository as a Claude Code plugin marketplace:

```text
/plugin marketplace add unnest-wintenboy/egovframe-guardian
/plugin install egovframe-guardian@egovframe-guardian
```

For local testing before installation:

```bash
claude --plugin-dir .
```

The Claude Code marketplace catalog lives at:

```text
.claude-plugin/marketplace.json
```

The Claude Code plugin manifest lives at:

```text
.claude-plugin/plugin.json
```

## How To Use

Use the bundled skill when a task involves:

- eGovFrame classic MVC development
- eGovFrame Boot REST services
- MyBatis mapper design
- login and Spring Security flows
- batch jobs
- MSA examples
- compatibility checks
- source refresh against official portal and GitHub repositories

Typical prompts:

```text
Use eGovFrame Guardian to review this service and mapper layout.
```

```text
Use eGovFrame Guardian to build a Boot REST CRUD example with MyBatis.
```

```text
Use eGovFrame Guardian to check whether this project follows eGovFrame transaction and mapper conventions.
```

## Hook Guardrails

The plugin installs `hooks/hooks.json` with lifecycle hooks for Codex and Claude-compatible plugin environments.

- `SessionStart`: announces that the bundled skill and guardrails are available.
- `UserPromptSubmit`: adds eGovFrame context when prompts mention eGovFrame, MyBatis, runtime, development environment, operating environment, common components, mobile, compatibility, AI RAG, VS Code, Istio, OpenTelemetry, or Flutter device APIs.
- `PreToolUse`: blocks destructive shell commands touching eGovFrame or plugin-critical paths unless the user explicitly confirms and the command includes `egovframe-guardian:allow-destructive`.
- `PermissionRequest`: denies approval requests for destructive commands touching eGovFrame or plugin-critical paths.
- `PostToolUse`: runs the guard scanner after file edit/write tools.
- `SubagentStart`: gives subagents the same portal-aligned eGovFrame context.
- `SubagentStop`: stops subagents from finishing when tracked eGovFrame findings remain.
- `PostCompact`: restores eGovFrame guard context after conversation compaction.
- `Stop`: checks the current root plus tracked plugin data before the agent ends the turn and asks the agent to continue once when blocking findings remain.

Plugin hooks are local guardrails. Users should review and trust hook definitions before enabling them.

## Scanner Rules

The scanner checks:

- controllers containing inline SQL or direct `JdbcTemplate` / `SqlSession` access
- MyBatis mapper XML files without `namespace`
- literal secret-like values in config files
- write-oriented service implementations without transaction boundaries
- mapper XML without mapper discovery configuration
- detected eGovFrame projects without explicit eGovFrame runtime dependency metadata

Run manually:

```bash
python scripts/egovframe_guard.py --mode scan --root .
```

In direct scan mode, high-confidence errors return exit code `2`; warnings return exit code `0`. In hook mode, the plugin returns structured hook JSON so the host can add context, deny supported tool calls, or continue the turn through the hook contract.

## Configuration

Default scanner policy lives at:

```text
config/egovframe-guardian.json
```

Projects can override noisy rules by adding:

```text
.egovframe-guardian.json
```

Rule severities and suppressions are data-driven so teams can tune findings without editing scanner code.

## Release And CI/CD

Pull requests and pushes run:

- JSON validation
- Python compile checks
- strict `basedpyright`
- bundled skill validation
- eGovFrame reference coverage audit
- pytest
- coverage gate
- maturity score
- public release metadata validation

Tag releases with semantic version tags:

```bash
git tag v0.1.0
git push origin v0.1.0
```

The release workflow packages the plugin, publishes `.zip` and `.tar.gz` archives, emits SHA-256 checksums, and creates a GitHub Release.

## Validate Locally

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

## Repository Layout

```text
.agents/plugins/marketplace.json      Codex marketplace catalog
.codex-plugin/plugin.json             Codex plugin manifest
.claude-plugin/plugin.json            Claude Code plugin manifest
.claude-plugin/marketplace.json       Claude Code marketplace catalog
hooks/hooks.json                      Lifecycle hook configuration
scripts/egovframe_guard.py            Scanner and hook entrypoint
skills/egovframe-developer/           Bundled eGovFrame skill and references
tests/                                Guard and hook tests
```

## Source Attribution

This plugin contains derived summaries, indexes, and examples based on:

- eGovFrame portal: <https://www.egovframe.go.kr/home/main.do>
- eGovFrame GitHub organization: <https://github.com/egovframework>

Bundled crawl records and repository atlases are for development guidance. Original upstream project materials remain under their respective source terms.

## Limitations

eGovFrame Guardian is a development aid. It does not replace official eGovFrame documentation, project-specific architecture review, security review, or compatibility testing. Static checks can produce false positives and false negatives.

Official Codex Plugin Directory self-serve publishing is not generally available yet, so this repository publishes a public self-hosted Codex marketplace catalog. Claude Code community marketplace submission still requires Anthropic review after local validation.
