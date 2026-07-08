# Development Playbook

## Selection Matrix

| Requirement | Start From | Primary References |
| --- | --- | --- |
| Legacy/classic web with JSP | `egovframe-common-components`, `egovframe-simple-homepage-template`, `egovframe-web-sample` | Runtime `Presentation`, `Persistence`, common components |
| Boot REST API | `egovframe-template-simple-backend`, `egovframe-boot-sample-java-config` | Boot sample Java config, mapper/service/controller layers |
| React + backend split | `egovframe-template-simple-react` and `egovframe-template-simple-backend` | React client + Boot REST boundary |
| MSA/cloud-native | `egovframe-msa-edu`, `egovframe-msa-common-components`, `egovframe-operating-environment-msa` | ConfigServer, EurekaServer, GatewayServer, service modules |
| Batch processing | `egovframe-runtime/Batch`, `egovframe-hands-on-guide` batch labs | Batch job config, reader/processor/writer |
| Mobile device APIs | `egovframe-mobile-device-api`, legacy device API repo | Device app/web split |
| AI/RAG | `egovframe-ai-rag` | Spring AI or LangChain4j sample modules |
| Compatibility confirmation | Portal `호환성확인` records | Compatibility application/service flow and SW catalog |

## Layering Rules

Use the target project’s package names and module style. Keep the standard layer order:

1. Controller or route boundary receives HTTP/UI input and converts it to typed request objects.
2. Service owns business transaction flow and calls mapper/repository abstractions.
3. Mapper/repository owns SQL or persistence calls. Keep SQL in mapper XML when the project uses MyBatis XML.
4. Domain/value objects carry state between layers. Do not put request parsing or DB-specific details in domain objects.
5. Configuration lives under existing Spring XML, Java config, `application.properties`, or `application.yml` according to the project.
6. Tests mirror the layer. Unit-test service logic, mapper-test SQL integration, and drive at least one controller/API path.

## Classic MVC Pattern

Use this for JSP/Spring MVC projects:

- Controller: `@Controller`, `@RequestMapping`, model population, validation result handling.
- Service: interface plus `@Service` implementation when the project follows the classic eGovFrame style.
- Mapper: `@Mapper` interface plus XML mapper under `src/main/resources`.
- View: JSP under the existing `/WEB-INF/jsp` convention.
- SQL: keep vendor-specific DDL/DML under the existing `DATABASE` or `script` convention.

## Boot REST Pattern

Use this for Boot templates and modern backend services:

- Controller: `@RestController`, request/response DTOs, status-aware responses.
- Service: transaction boundary with `@Transactional` on write operations.
- Mapper: MyBatis mapper XML or annotation style matching the target.
- Config: `application.properties` or `application.yml`, not hard-coded datasource values.
- Test: `@WebMvcTest` for boundary behavior and mapper integration tests when SQL changes.

## MSA Pattern

Use this for MSA/common-component services:

- Keep ConfigServer, EurekaServer, GatewayServer, and service modules separate.
- Externalize service ports, datasource URLs, discovery URLs, and gateway route IDs.
- Keep service-local persistence inside the service module.
- Use Docker/Kubernetes manifests already present in the repo as the deployment style source.
- Verify service route, config loading, discovery registration, and container config.

## Common Component Extension Pattern

When extending common components:

- Locate the matching component module or package first; do not create parallel packages.
- Preserve menu, authorization, login, code, board, questionnaire, search, and mobile ID conventions.
- Add database migration or seed SQL next to the existing component scripts.
- Add UI messages and i18n entries where the component already keeps them.
- Check security and authorization filters before exposing a new endpoint.

## Compatibility and Download Work

When the user asks about downloads, versions, compatibility SW, or certification:

- Read `portal-manual-map.md` first.
- Read `portal-zip-inventory.md` when the question is about ZIP attachments, package names, checksums, or whether a portal archive is covered.
- Read `distribution-file-playbook.md` before using, extracting, or adapting files from a downloaded distribution package.
- Search `portal-crawl-records.json` for the exact menu label or product/version.
- Preserve source URL, captured date, and whether the record came from a paginated board.
- ZIP archives are represented by filename, page URL, attachment URL when captured, size text, and checksum text. Do not claim to know internal file trees unless the ZIP has actually been downloaded and inspected.
- Avoid downloading binary attachments unless the user explicitly asks for the files. If downloading is needed, verify the portal checksum when present, run `python scripts/egovframe_distribution.py inspect --zip <file> --json`, extract only to a temporary/sandbox directory, and never execute bundled scripts automatically.
- For source-project distributions, apply a curated diff: build files first, then config, mapper/XML, SQL, controller/API, view/client assets, and tests. Do not overwrite the target project wholesale.

## Implementation Checklist

- Match the official repo closest to the requested architecture.
- Inspect current target files before editing.
- Use examples from `assets/examples/` only as starting points.
- Replace package names, table names, DTO fields, validation rules, and datasource names.
- Add tests at the layer touched by the change.
- Run the real build or route/test surface.
- Run `scripts/audit_coverage.py` when updating this skill’s bundled sources.
