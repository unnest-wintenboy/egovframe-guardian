# Coverage Protocol

## Required Coverage

The skill bundle is considered complete only when these checks pass:

- Portal crawl JSON exists and parses.
- Portal sections include all six requested areas.
- Portal record count is at least the captured baseline of 751.
- GitHub manifest exists and parses.
- Repository atlas includes all captured public repositories.
- Repository directory index includes directory counts for every repo.
- Example asset directories exist for classic MVC, Boot REST, MSA, batch, security, and React client patterns.
- `SKILL.md` frontmatter validates with the system skill validator.

## Review Loop

Run the loop whenever updating the skill:

1. Run `python scripts/audit_coverage.py --skill-dir .`.
2. Fix missing sources, references, or examples.
3. Run the system quick validator.
4. Re-read `SKILL.md` and confirm every referenced file exists.
5. Sample at least one example asset and one generated reference.
6. Repeat until the audit and validator are clean.

## Known Captured Caveats

- Some public portal boards are intentionally not fully fanned out because they have hundreds or thousands of records.
- Binary downloads are represented by URLs and labels, not embedded files.
- `egovframe-msa-common-components` may show immediate checkout modifications on Windows due to upstream `.gitattributes` line-ending rules on assets.
