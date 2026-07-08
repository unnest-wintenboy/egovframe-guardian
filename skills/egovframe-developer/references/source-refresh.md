# Source Refresh

Use this process when eGovFrame updates or when a user asks for the latest standard.

## Portal Manuals

1. Re-crawl `https://www.egovframe.go.kr/home/main.do`.
2. Preserve the six primary sections: 표준프레임워크 소개, 개발가이드, 다운로드, 개발자 참여, 기술지원, 호환성확인.
3. Keep large-board behavior explicit. If a board is too large to fan out politely, record the count and first-list URL.
4. Regenerate:
   - `references/portal-crawl-records.json`
   - `references/portal-manual-map.md`
5. Run `scripts/audit_coverage.py --skill-dir .`.

## GitHub Repositories

1. Enumerate `https://api.github.com/orgs/egovframework/repos?type=public&per_page=100`.
2. Clone new repos into the local source workspace or update existing clones with `git fetch --all --prune`.
3. Rebuild the directory atlas from tracked files, not from filesystem leftovers.
4. Regenerate:
   - `references/github-clone-manifest.json`
   - `references/repository-directory-index.json`
   - `references/repository-directory-atlas.md`
5. Re-run the coverage audit.

## Update Discipline

- Never delete old coverage silently. Mark removed upstream repos/pages as removed with date/source if historical trace matters.
- Prefer official portal/GitHub sources over third-party posts.
- Capture source URL and crawl/fetch time.
- Keep `SKILL.md` stable and move volatile details into references.
- If a standard changes, update examples only after comparing the closest official repo/template.
