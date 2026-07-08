# eGovFrame Guardian

eGovFrame Guardian is a Codex plugin for building, reviewing, and maintaining projects that follow the Korean eGovFrame standard framework.

It packages:

- The `egovframe-developer` skill with official portal crawl records, repository atlas, examples, and coverage audit.
- A local hook-driven guard scanner for common eGovFrame standard violations.
- Release-readiness tests and maturity scoring for plugin distribution.

## Status

Current release label: `v0.1.0-internal-beta`.

The plugin is ready for local use, internal team beta, and private GitHub source control. Before public marketplace submission, make the repository public if required by the target marketplace and add public website, privacy, and terms URLs to the manifest.

## Install Locally

The personal marketplace entry points to:

```text
C:\Users\SIL\.agents\plugins\marketplace.json
```

The plugin root is:

```text
C:\Users\SIL\plugins\egovframe-guardian
```

After installing or updating through the Codex plugin UI, start a new Codex thread so plugin skills and hooks are loaded from the cache.

## Main Skill

Use the bundled `egovframe-developer` skill when the task involves:

- eGovFrame classic MVC development
- eGovFrame Boot REST services
- MyBatis mapper design
- security login flows
- batch jobs
- MSA examples
- compatibility checks
- source refresh against official portal and GitHub repositories

## Hook Guardrails

The plugin installs `hooks/hooks.json` with:

- `SessionStart`: announces that the bundled skill and guardrails are available.
- `UserPromptSubmit`: adds portal-aligned eGovFrame context when prompts mention eGovFrame, eGovFramework, MyBatis, runtime, development environment, operating environment, common components, mobile, compatibility, AI RAG, VS Code, Istio, OpenTelemetry, or Flutter device APIs.
- `PreToolUse`: blocks destructive shell commands touching eGovFrame or plugin-critical paths unless the user explicitly confirms and the command includes `egovframe-guardian:allow-destructive`.
- `PermissionRequest`: denies approval requests for destructive commands touching eGovFrame or plugin-critical paths.
- `PostToolUse`: runs the guard scanner after file edit/write tools.
- `SubagentStart`: gives subagents the same portal-aligned eGovFrame context.
- `SubagentStop`: stops subagents from finishing when tracked eGovFrame findings remain.
- `PostCompact`: restores eGovFrame guard context after conversation compaction.
- `Stop`: checks the current root plus tracked `PLUGIN_DATA` scan state before Codex ends the turn and asks Codex to continue once when blocking findings remain.

The prompt and subagent context follows the current portal surface: standard framework introduction and architecture, development guide, downloads, developer participation, technical support, compatibility confirmation, and current v5.0.0 highlights such as VS Code Extension, AI RAG examples, Istio/OpenTelemetry operating guides, and Flutter device API programs.

The scanner checks:

- controller inline SQL or direct `JdbcTemplate` / `SqlSession` access
- MyBatis mapper XML without `namespace`
- literal secret-like values in config files
- write-oriented service implementations without transaction boundaries
- mapper XML without mapper discovery configuration
- eGovFrame project signals without runtime dependency metadata

In direct scan mode, high-confidence errors return exit code `2` and warnings return exit code `0`.
In hook mode, the plugin returns Codex hook JSON instead of failing with raw text so Codex can add context, deny supported tool calls, or continue the turn through the official hook contract.

## Hook Policy

Default policy lives at:

```text
config/egovframe-guardian.json
```

Rule severities and suppressions are intentionally data-driven so projects can tune noisy warnings without editing the scanner.

Hook session state is stored in Codex-provided `PLUGIN_DATA` when available. The state records eGovFrame roots touched by supported hooks and their most recent scan result, so final gates can catch findings even when the active `cwd` has moved.

## Commands

Run the scanner:

```bash
python scripts/egovframe_guard.py --mode scan --root .
```

Smoke-test a destructive-command hook response:

```bash
echo '{"tool_name":"Bash","tool_input":{"command":"rm -rf src/main/java/egovframework"}}' | python scripts/egovframe_guard.py --mode pre-tool
```

Smoke-test a permission request denial:

```bash
echo '{"tool_name":"Bash","tool_input":{"command":"git clean -fd src/main/resources/egovframework"}}' | python scripts/egovframe_guard.py --mode permission
```

Run maturity scoring:

```bash
python scripts/score_maturity.py . --fail-under 110
```

Run tests with uv:

```bash
uv run --with pytest pytest
```

Fallback when pytest is already installed:

```bash
python -m pytest
```

## Verification

Expected release checks:

- plugin manifest validates
- JSON files parse
- Python scripts compile
- bundled skill validates with UTF-8 mode
- coverage audit passes
- guard tests and core/hook/state coverage gates pass
- maturity score is `110 / 110`

On Windows, use `PYTHONUTF8=1` when running the skill validator because the bundled Korean UTF-8 content can fail under the default `cp949` codec.

The Python type gate runs `basedpyright` in `typeCheckingMode = "all"` and keeps `Unknown` checks enabled. `reportAny` is disabled only because the standard-library `json.loads` return type is `Any`; JSON boundaries are immediately narrowed into the local `JsonValue` alias.

## Source Attribution

This plugin contains derived summaries, indexes, and examples based on:

- eGovFrame portal: <https://www.egovframe.go.kr/home/main.do>
- eGovFrame GitHub organization: <https://github.com/egovframework>

Bundled crawl records and repository atlases are for development guidance. The original upstream project materials remain under their respective source terms.

## Distribution Maturity Score

`scripts/score_maturity.py` measures local/internal distribution completeness. A score of `110 / 110` means the local plugin package has metadata, docs, tests, CI, hook policy, bundled assets, and release-readiness checks. It does not mean a public marketplace has accepted the plugin.

## Public Release Checklist

- Add public website, privacy, and terms URLs when preparing a public marketplace submission.
- Keep `LICENSE`, `README.md`, `CHANGELOG.md`, `SECURITY.md`, tests, and CI workflow in the release branch.
- Tag releases semantically.
- Run `scripts/score_maturity.py . --fail-under 110`.
- Run the guard test suite on Windows and Linux.
- Run `uv run --with pytest --with pytest-cov pytest --cov=egovframe_guard_core --cov=egovframe_guard_hooks --cov=egovframe_guard_state --cov-report=term-missing --cov-fail-under=80`.
- Run a marketplace scanner if submitting to a curated list.
