<p align="right">
  <strong>English</strong> | <a href="README.md">한국어</a>
</p>

# eGovFrame Guardian

<p align="center">
  <img src="assets/egovframe-guardian-mascot.png" alt="eGovFrame Guardian mascot" width="180">
</p>

<p align="center">
  <a href="https://github.com/unnest-wintenboy/egovframe-guardian/actions/workflows/ci.yml"><img alt="CI" src="https://github.com/unnest-wintenboy/egovframe-guardian/actions/workflows/ci.yml/badge.svg"></a>
  <a href="https://github.com/unnest-wintenboy/egovframe-guardian/actions/workflows/release.yml"><img alt="Release" src="https://github.com/unnest-wintenboy/egovframe-guardian/actions/workflows/release.yml/badge.svg"></a>
  <a href="https://github.com/unnest-wintenboy/egovframe-guardian/releases"><img alt="GitHub release" src="https://img.shields.io/github/v/release/unnest-wintenboy/egovframe-guardian?label=release"></a>
  <a href="LICENSE"><img alt="License: MIT" src="https://img.shields.io/badge/license-MIT-green.svg"></a>
  <img alt="Codex plugin" src="https://img.shields.io/badge/Codex-plugin-0f172a">
  <img alt="Claude Code plugin" src="https://img.shields.io/badge/Claude%20Code-plugin-5b21b6">
</p>

<p align="center">
  <strong>A gentle guardrail kit for agents working on Korean eGovFrame projects.</strong>
  <br>
  Build, review, scan, and ship eGovFrame-aligned code from Codex or Claude Code.
</p>

eGovFrame Guardian gives coding agents the context they usually miss: official eGovFrame portal notes, GitHub repository indexes, practical Java examples, and local hooks that catch common framework drift before it turns into review pain.

Use it when the work touches classic MVC, eGovFrame Boot, MyBatis, Spring Security, batch, MSA, compatibility checks, or public-sector Java maintenance.

## Why This Exists

eGovFrame projects often fail in the quiet places: mapper namespaces, transaction boundaries, runtime metadata, SQL leaking into controllers, and examples copied from the wrong generation of the framework. This plugin keeps those details close to the agent while it edits, reviews, and prepares releases.

It is intentionally boring where boring is good: data-driven rules, reproducible validation, CI gates, signed release checksums, and source attribution back to the official eGovFrame portal and organization.

## Quick Start

Install the marketplace, enable the plugin, then ask the agent to use `eGovFrame Guardian`.

### Codex

```bash
codex plugin marketplace add unnest-wintenboy/egovframe-guardian
```

Open the Codex plugin directory, choose **eGovFrame Guardian**, review the hook definitions, and enable it.

### Claude Code

```text
/plugin marketplace add unnest-wintenboy/egovframe-guardian
/plugin install egovframe-guardian@egovframe-guardian
```

For local plugin testing:

```bash
claude --plugin-dir .
```

Plugin hooks run locally. Review and trust the hook definitions before enabling them in either host.

## What You Get

| Name | Plain meaning | When to use it |
| --- | --- | --- |
| `egovframe-developer` skill | A work guide that helps the agent follow eGovFrame patterns | When asking for implementation, review, migration, or compatibility checks |
| Portal-based references | Easy-to-use notes based on official eGovFrame material | When you want the agent to avoid generic Spring-only answers |
| Example code | Ready shapes for MVC, Boot REST, MyBatis, security, batch, and MSA work | When starting a new feature or asking for a reference implementation |
| Hook guardrails | Safety checks that run automatically while the agent works | When you want risky commands blocked and edits checked right away |
| Scanner | A checker for common eGovFrame mistakes | When checking controller SQL, mapper namespaces, transactions, and runtime metadata |
| CI/CD | Automated validation before public release | When publishing the plugin or cutting a release |

## How To Use The Skill

The skill is not a separate app button. It is a work mode you name in your prompt. After enabling the plugin, mention `eGovFrame Guardian` or `egovframe-developer` in the request.

Good prompts can stay short and direct.

```text
Use eGovFrame Guardian to review this service and mapper layout.
```

```text
Use eGovFrame Guardian to build an eGovFrame Boot REST CRUD example with MyBatis.
```

```text
Use eGovFrame Guardian to check whether this project follows eGovFrame transaction, mapper, and runtime metadata conventions.
```

```text
Use eGovFrame Guardian to migrate this controller/service/mapper flow toward the current standard.
```

The agent reads the bundled skill and uses the portal notes, repo indexes, example code, and scanner rules together. For best results, include the goal, target folder, eGovFrame version, and whether the project is classic MVC or Boot.

## When And Why Hooks Run

Hooks are not commands you run by hand. Codex or Claude Code calls them automatically at specific points while the agent works. Their job is to keep eGovFrame context close and stop risky actions before they cause damage.

| When it runs | Why it exists | What happens |
| --- | --- | --- |
| Session start `SessionStart` | The agent should know the plugin is active right away | It announces that the eGovFrame skill and guardrails are ready |
| Prompt submit `UserPromptSubmit` | Prompts that mention eGovFrame, MyBatis, runtime, or compatibility need framework context | It adds portal-aligned context so the answer does not drift into generic Spring guidance |
| Before a tool call `PreToolUse` | Delete, move, and overwrite commands can be hard to recover from | It blocks destructive commands against eGovFrame or plugin-critical paths |
| Permission request `PermissionRequest` | Risky commands should be filtered before approval | It denies destructive approval requests for protected paths |
| After edits or writes `PostToolUse` | Problems are cheapest to fix right after code changes | It runs the scanner for controller SQL, mapper, transaction, secret, and metadata issues |
| Subagent start `SubagentStart` | Other agents need the same standard | It gives subagents the same eGovFrame context |
| Subagent stop `SubagentStop` | Findings should not be left behind quietly | It prevents subagents from finishing while tracked findings remain |
| After compaction `PostCompact` | Long conversations can lose important context after compaction | It restores the eGovFrame guard context |
| Before turn end `Stop` | Blocking findings deserve one final check | It asks the agent to continue once when unresolved findings remain |

If a destructive shell command is truly needed, the command must include `egovframe-guardian:allow-destructive`. That token is an intentional confirmation step, not a normal everyday option.

## Scanner Rules

Run the scanner directly:

```bash
python scripts/egovframe_guard.py --mode scan --root .
```

It currently checks for:

- inline SQL or direct `JdbcTemplate` / `SqlSession` access inside controllers
- MyBatis mapper XML files without `namespace`
- literal secret-like values in config files
- write-oriented service implementations without transaction boundaries
- mapper XML files without mapper discovery configuration
- detected eGovFrame projects without explicit eGovFrame runtime dependency metadata

In direct scan mode, high-confidence errors return exit code `2`; warnings return exit code `0`. In hook mode, the plugin returns structured hook JSON so the host can add context, deny supported tool calls, or continue the turn through the hook contract.

## Configuration

Default scanner policy lives at:

```text
config/egovframe-guardian.json
```

Projects can override noisy rules with:

```text
.egovframe-guardian.json
```

Rule severities and suppressions are data-driven, so teams can tune findings without editing scanner code.

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

## Release Flow

Pull requests and pushes run JSON validation, Python compile checks, strict `basedpyright`, bundled skill validation, reference coverage audit, pytest, coverage, maturity scoring, and public release metadata validation.

Tag releases with semantic version tags:

```bash
git tag vX.Y.Z
git push origin vX.Y.Z
```

The release workflow publishes `.zip` and `.tar.gz` archives, emits SHA-256 checksums, and creates a GitHub Release.

## Repository Map

```text
README.md                             Korean default README
README.en.md                          English README
.agents/plugins/marketplace.json      Codex marketplace catalog
.codex-plugin/plugin.json             Codex plugin manifest
.claude-plugin/plugin.json            Claude Code plugin manifest
.claude-plugin/marketplace.json       Claude Code marketplace catalog
assets/egovframe-guardian-mascot.png  README mascot logo
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

## License

The code, documentation, and generated mascot asset in this repository are distributed under the [MIT License](LICENSE). Upstream eGovFrame materials referenced or summarized by this plugin remain under their own source terms.

## Current Publishing Notes

This repository publishes a public self-hosted Codex marketplace catalog because official Codex Plugin Directory self-serve publishing is not generally available yet. Claude Code community marketplace submission still requires Anthropic review after local validation.

## Limitations

eGovFrame Guardian is a development aid. It does not replace official eGovFrame documentation, project-specific architecture review, security review, or compatibility testing. Static checks can produce false positives and false negatives.
