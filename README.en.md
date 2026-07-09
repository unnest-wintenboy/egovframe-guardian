<p align="right">
  <strong>English</strong> | <a href="README.md">한국어</a>
</p>

# eGovFrame Guardian

<p align="center">
  <img src="assets/egovframe-guardian-mascot-retro.png" alt="eGovFrame Guardian retro pixel mascot" width="180">
</p>

<p align="center">
  <a href="https://github.com/unnest-wintenboy/egovframe-guardian/releases"><img alt="GitHub release" src="https://img.shields.io/github/v/release/unnest-wintenboy/egovframe-guardian?label=release"></a>
  <a href="LICENSE"><img alt="License: MIT" src="https://img.shields.io/badge/license-MIT-green.svg"></a>
  <img alt="Codex plugin" src="https://img.shields.io/badge/Codex-plugin-0f172a">
  <img alt="Claude Code plugin" src="https://img.shields.io/badge/Claude%20Code-plugin-5b21b6">
</p>

<p align="center">
  <strong>A gentle guardrail kit for agents working on Korean eGovFrame projects.</strong>
  <br>
  Build, review, and scan eGovFrame-aligned code from Codex or Claude Code.
</p>

eGovFrame Guardian gives coding agents the context they usually miss: official eGovFrame portal notes, GitHub repository indexes, practical Java examples, and local hooks that catch common framework drift before it turns into review pain.

Use it when the work touches classic MVC, eGovFrame Boot, MyBatis, Spring Security, batch, MSA, compatibility checks, or public-sector Java maintenance.

## Why This Exists

eGovFrame projects often fail in the quiet places: mapper namespaces, transaction boundaries, runtime metadata, SQL leaking into controllers, and examples copied from the wrong generation of the framework. This plugin keeps those details close to the agent while it edits, reviews, and maintains the project.

It is intentionally boring where boring is good: data-driven rules, reproducible checks, and source attribution back to the official eGovFrame portal and organization.

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
| ZIP download and distribution use | Notes for portal ZIP filenames, page URLs, attachment URLs, sizes, checksums, and safe pre-extraction inspection | When applying a standard framework distribution package to a project |
| Loop engineering guide | A way to split larger work into bounded iterations with evidence and verification each time | When implementation, review, migration, or ZIP adoption cannot be done safely in one pass |
| Hook guardrails | Safety checks that run automatically while the agent works | When you want risky commands blocked and edits checked right away |
| Scanner | A checker for common eGovFrame mistakes | When checking controller SQL, mapper namespaces, transactions, and runtime metadata |

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

The agent reads the bundled skill and uses the portal notes, repo indexes, example code, and scanner rules together. For larger work, it follows a short `goal -> evidence -> plan -> act -> observe -> verdict` loop and records passed checks plus remaining gaps. For best results, include the goal, target folder, eGovFrame version, and whether the project is classic MVC or Boot.

## When And Why Hooks Run

Hooks are not commands you run by hand. Codex or Claude Code calls them automatically at specific points while the agent works. Their job is to keep eGovFrame context close and stop risky actions before they cause damage.

| When it runs | Why it exists | What happens |
| --- | --- | --- |
| Session start `SessionStart` | The agent should know the plugin is active right away | It announces that the eGovFrame skill and guardrails are ready |
| Prompt submit `UserPromptSubmit` | Prompts that mention eGovFrame, egovframework, or the Korean standard framework need framework context | It adds portal-aligned context so the answer does not drift into generic Spring guidance |
| Before a tool call `PreToolUse` | Delete, move, and overwrite commands can be hard to recover from | It blocks destructive commands against eGovFrame or plugin-critical paths |
| Permission request `PermissionRequest` | Risky commands should be filtered before approval | It denies destructive approval requests for protected paths |
| After edits or writes `PostToolUse` | Problems are cheapest to fix right after code changes | It runs the scanner for controller SQL, mapper, transaction, secret, and metadata issues |
| Subagent start `SubagentStart` | Other agents working on eGovFrame need the same standard | It adds context only when the subagent request includes eGovFrame signals |
| Subagent stop `SubagentStop` | Already-found issues should not be left behind quietly | It blocks only when tracked blocking findings remain for the current project |
| After compaction `PostCompact` | Long conversations can lose important context after compaction | It restores the eGovFrame guard context |
| Before turn end `Stop` | Previously tracked blocking findings deserve one final check | It asks the agent to continue only when recorded findings remain unresolved for the current project |

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

## Distribution ZIP Inspection

When you download a ZIP from the eGovFrame portal, inspect it before extracting it.

```bash
python scripts/egovframe_distribution.py inspect --zip path/to/package.zip --expected-sha1 <portal-sha1> --json
```

The inspector reports checksum status, ZIP-slip path risks, executable/script entries, Maven/Gradle/Spring/MyBatis/JSP/SQL signals, and the likely distribution type. For source-project ZIPs, extract into a temporary folder and apply only the needed controller, service, mapper, config, and SQL pieces.

To summarize ZIP coverage in the bundled portal crawl:

```bash
python scripts/egovframe_distribution.py inventory --portal-json skills/egovframe-developer/references/portal-crawl-records.json --json
```

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

## Maintainer Notes

If you are modifying or publishing the plugin, see [development notes](docs/development.md). Most users only need the install and usage sections above.

## Source Attribution

This plugin contains derived summaries, indexes, and examples based on:

- eGovFrame portal: <https://www.egovframe.go.kr/home/main.do>
- eGovFrame GitHub organization: <https://github.com/egovframework>

Bundled crawl records and repository atlases are for development guidance. Original upstream project materials remain under their respective source terms.

## License

The code, documentation, and generated mascot asset in this repository are distributed under the [MIT License](LICENSE). Upstream eGovFrame materials referenced or summarized by this plugin remain under their own source terms.

## Limitations

eGovFrame Guardian is a development aid. It does not replace official eGovFrame documentation, project-specific architecture review, security review, or compatibility testing. Static checks can produce false positives and false negatives.
