# Distribution File Playbook

Use this playbook when a task involves an eGovFrame portal ZIP, release package, developer environment bundle, runtime library archive, common component distribution, mobile package, or downloaded source archive.

## Why This Exists

The official portal publishes ZIP packages across runtime downloads, developer environment downloads, common component downloads, mobile downloads, and classified common component downloads. These pages commonly include filenames, attachment sizes, and MD5/SHA1 checksum text. A ZIP filename alone is not enough to trust or apply the package.

Treat every distribution file as an external input:

1. Identify it from `portal-zip-inventory.md` or the live portal page.
2. Capture the source page URL, filename, visible size text, release date, and checksum text.
3. Download only when the user explicitly needs the package.
4. Inspect the archive before extraction.
5. Extract only into a temporary or sandbox directory.
6. Never execute bundled scripts, installers, binaries, JAR/WAR/EAR files, or IDE plugins automatically.

## Inspection Command

After the ZIP is downloaded, run:

```bash
python scripts/egovframe_distribution.py inspect --zip path/to/package.zip --expected-sha1 <portal-sha1> --json
```

Use `--expected-md5`, `--expected-sha1`, or `--expected-sha256` according to the hash provided by the portal page.

To summarize the bundled portal crawl coverage:

```bash
python scripts/egovframe_distribution.py inventory --portal-json skills/egovframe-developer/references/portal-crawl-records.json --json
```

The inspection report classifies the archive using internal signals:

Archives with ZIP-slip style paths such as `../outside.txt`, absolute paths, drive-letter paths, or NUL bytes must be rejected before extraction.

| Signal | Meaning | Use it for |
| --- | --- | --- |
| `maven-project` | `pom.xml` exists | Source project, sample, common component, or runtime source review |
| `gradle-project` | Gradle build files exist | Boot/MSA or modern sample review |
| `spring-config` | `application.properties`, `application.yml`, or `application.yaml` exists | Datasource, profile, and config migration |
| `mybatis-mapper` | Mapper or sqlmap XML exists | Mapper namespace and SQL review |
| `jsp-webapp` | JSP or `WEB-INF` exists | Classic MVC/common component UI review |
| `sql-script` | SQL scripts exist | Schema, seed, and migration planning |
| `docker` / `kubernetes` | Container manifests exist | MSA/operating environment deployment checks |
| `eclipse-plugin-bundle` | Eclipse `plugins/`, `features/`, or `.eclipseproduct` exists | Manual developer tooling installation only |
| `script-or-binary` | Executable, script, JAR, WAR, EAR, or native library exists | Manual review; do not auto-execute |

## Decision Matrix

| Distribution type | Typical source | Agent behavior |
| --- | --- | --- |
| `source-project` | Boot starter source, common component all-in-one, examples, mobile server packages | Inspect, extract to sandbox, review build/config/layer layout, copy only selected files, then run project build and guardian scan |
| `developer-tooling` | Eclipse plugin binary/source ZIP, development environment package | Verify checksum and report install notes; do not install or run automatically |
| `binary-package` | Runtime library archive, JAR/WAR/EAR-containing package, installer bundle | Prefer dependency coordinates or documented install flow; do not vendor binaries unless the user explicitly asks |
| `documentation` | Javadoc or manual package | Use as reference material; preserve source attribution |
| `archive` | Unknown or mixed ZIP | Inspect listing, ask for intent if the report is ambiguous, and keep extraction sandboxed |

## Applying A Source Package

For source-oriented packages, do not overwrite the target project wholesale. Work in this order:

1. Extract to a temporary or clearly named sandbox folder.
2. Read build files first: `pom.xml`, `build.gradle`, `settings.gradle`, dependency versions, Java version, and eGovFrame runtime version.
3. Read configuration next: Spring XML, Java config, `application.properties`, `application.yml`, datasource profiles, mapper scanning, security config, and batch config.
4. Read persistence assets: MyBatis mapper XML, repository interfaces, SQL scripts, and migration folders.
5. Read web/API assets: controllers, DTOs, JSP files, REST endpoints, filters, and interceptors.
6. Copy or adapt only the files needed for the user's target architecture.
7. Run the target project's build/test command and `python scripts/egovframe_guard.py --mode scan --root <target>`.

## Package-Specific Notes

### Runtime Library ZIP

Prefer Maven/Gradle dependency declarations over copying binary libraries into a project. Confirm the eGovFrame version, Spring version family, and JDK requirement from the portal page. If a runtime ZIP includes source or Javadoc, inspect and cite it as reference material rather than treating it as a template.

### Developer Environment ZIP

Developer environment packages may contain Eclipse plugins, features, binaries, and platform-specific bundles. Verify the checksum and summarize the matching Eclipse version and OS target. Installation is a manual user action.

### Common Component ZIP

Common component all-in-one packages often include source, JSP, mapper XML, SQL, configuration, and security patch notes. Apply them as a curated diff:

- identify the exact component and version,
- compare database scripts before applying,
- preserve local menu, auth, code, and message conventions,
- run scanner checks after adaptation.

### MSA And Operating Environment ZIP

Look for ConfigServer, EurekaServer, GatewayServer, Docker, Kubernetes, and service module boundaries. Preserve service-local ownership. Validate ports, route IDs, discovery URLs, config repository paths, and container manifests.

### Mobile Package ZIP

Separate app, server, and web common component packages. Keep mobile device APIs, server endpoints, and web assets in their original boundary unless the user asks for migration.

## Freshness Rule

Portal download pages change. For any request involving "latest", "current", "today", a specific release date, or a new package name, check the live portal page before giving an answer or applying a checksum.
