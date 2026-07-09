# eGovFrame Guardian Hook Rules

The plugin hooks add portal-aligned context, guard critical operations, scan after edits, restore context after compaction, and check tracked findings before Codex or a subagent stops.

- `UserPromptSubmit`: injects eGovFrame standard-development context for matching prompts.
- `PreToolUse`: denies destructive shell commands touching eGovFrame or plugin-critical paths unless explicitly confirmed with `egovframe-guardian:allow-destructive`.
- `PermissionRequest`: denies approval requests for destructive eGovFrame/plugin-critical commands.
- `PostToolUse`: runs a local scanner after file edit/write tools.
- `SubagentStart`: injects eGovFrame context only when the subagent task includes eGovFrame signals.
- `SubagentStop`: blocks subagent completion only when tracked findings for the current project remain.
- `PostCompact`: reminds Codex to reload eGovFrame context after compaction.
- `Stop`: asks Codex to continue once when tracked blocking findings or unscanned work remain for the current project.

Prompt/subagent context follows the portal surface: introduction/architecture, development guide, downloads, developer participation, technical support, compatibility confirmation, and current v5.0.0 highlights such as VS Code Extension, AI RAG examples, Istio/OpenTelemetry operating guides, and Flutter device APIs.

Scan mode exits non-zero for high-confidence errors; hook mode returns structured Codex hook JSON.

- `controller-sql`: controllers must not contain inline SQL or direct `JdbcTemplate`/`SqlSession` data access.
- `mapper-namespace`: MyBatis mapper XML files must declare a `namespace`.
- `plain-secret`: application/config files must not contain literal passwords, tokens, keys, or secrets.
- `service-transaction`: write-oriented service classes should declare transactional boundaries.
- `mapper-scan`: mapper interfaces and XML mapper locations should be discoverable by annotation or configuration.
- `egov-runtime`: detected eGovFrame projects should keep an explicit eGovFrame runtime dependency in build metadata.

Run manually:

```bash
python scripts/egovframe_guard.py --mode scan --root .
```
