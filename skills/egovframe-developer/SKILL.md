---
name: egovframe-developer
description: Build, modify, review, migrate, or troubleshoot applications that use the Korean eGovFrame/eGovFramework standard framework, including runtime, development environment, common components, Boot templates, MSA templates, mobile device APIs, compatibility confirmation, downloads, portal manuals, and official egovframework GitHub repositories. Use when the user asks for 표준프레임워크, eGovFrame, eGovFramework, 전자정부 표준프레임워크, 공통컴포넌트, 개발가이드, 다운로드, 호환성확인, or implementation according to the standard.
---

# eGovFrame Developer

## Operating Rule

Use official local evidence before relying on memory. Start from the bundled portal crawl and GitHub repository atlas, then inspect live project files or upstream sources as needed.

## Source Order

1. Load `references/portal-manual-map.md` for the portal/manual hierarchy, section coverage, and large-board caveats.
2. Load `references/repository-directory-atlas.md` for directory-level summaries of all cloned official GitHub repositories.
3. Search `references/repository-directory-index.json` when exact directory coverage is needed; it contains every tracked directory count from the 23 cloned repos.
4. Search `references/portal-crawl-records.json` when exact page text, URLs, tables, download links, or board counts are needed.
5. Load `references/portal-zip-inventory.md` when the task asks about portal ZIP attachments, checksums, release archives, or whether a download package is covered.
6. Load `references/development-playbook.md` before implementing or reviewing code.
7. Load `references/example-code-catalog.md` before copying from `assets/examples/`.
8. Run `scripts/audit_coverage.py` after editing this skill or when checking whether the source bundle still covers all captured manuals/repos.

## Workflow

1. Classify the task:
   - Classic web app: use runtime, common components, templates, JSP, MyBatis, Spring MVC.
   - Boot app: use Boot samples/templates, Java config, `application.properties`, REST/service/mapper layers.
   - MSA/cloud: use MSA education, MSA common components, config/eureka/gateway/service layout, Docker/Kubernetes.
   - Development tooling: use development environment, VS Code Initializr, Eclipse plugins, codegen templates.
   - Compatibility/download/support: use portal crawl records and compatibility pages.
2. Read the smallest matching reference first. Do not load the full JSON unless exact coverage or page text is required.
3. Inspect the target project structure before changing code. Match its build tool, package naming, XML/YAML style, mapper style, and test layout.
4. Prefer official sample structure over invented architecture. If the target repo already diverges, preserve local conventions unless they violate the standard or the user asks for migration.
5. Implement by layer: controller or API boundary, service/use case, persistence/mapper, config, tests, deployment notes.
6. Verify through the project’s real surface: Maven/Gradle build, unit/integration tests, HTTP route, UI flow, batch launch, or container manifest validation as applicable.
7. Record gaps explicitly. If a needed manual page is absent from the captured bundle, refresh sources rather than guessing.

## Reference Routing

| Need | Read |
| --- | --- |
| Portal menu/manual hierarchy | `references/portal-manual-map.md` |
| All official repo directory summaries | `references/repository-directory-atlas.md` |
| Exact repo directory coverage | `references/repository-directory-index.json` |
| Exact portal page/body/table/link text | `references/portal-crawl-records.json` |
| Portal ZIP/download package coverage | `references/portal-zip-inventory.md` |
| Development standards and layer patterns | `references/development-playbook.md` |
| Example code assets | `references/example-code-catalog.md` |
| Maintenance and refresh process | `references/source-refresh.md` |
| Coverage audit protocol | `references/coverage-protocol.md` |

## Example Assets

Copy only the examples that match the target architecture, then adapt package names, framework versions, datasource names, and build files to the target project:

- `assets/examples/classic-mvc-crud/`
- `assets/examples/boot-rest-crud/`
- `assets/examples/msa-service/`
- `assets/examples/batch-job/`
- `assets/examples/security-login/`
- `assets/examples/react-client/`

## Validation

Run:

```bash
python scripts/audit_coverage.py --skill-dir .
```

Require all checks to pass before claiming this skill still covers the captured standard source set. If the audit fails, update the relevant reference or source bundle first.
