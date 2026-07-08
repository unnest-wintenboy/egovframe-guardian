# Portal ZIP Inventory

Captured from: `references/portal-crawl-records.json`

## What Is Covered

The portal crawl captures ZIP download packages as metadata, not as embedded binaries.

Current captured bundle evidence:

- 751 portal records.
- 120 records mention at least one `.zip` filename.
- 360 distinct `.zip` filename mentions were found in captured page text.
- 685 MD5, 684 SHA1, and 22 SHA256 checksum mentions were found near download package text.
- 63 ZIP-bearing detail records include direct `readDownloadFile.do` attachment URLs.
- Large public board caveat: `다운로드 / 분류별 다운로드` reports 2,995 records and is intentionally not fully fanned out. Use the live page if a component-specific ZIP from that board is needed.

Primary ZIP-heavy surfaces:

| Portal area | Representative page | ZIP evidence |
| --- | --- | --- |
| 실행환경 다운로드 | `https://www.egovframe.go.kr/home/sub.do?menuNo=106` | runtime, Boot starter, source, javadoc, lite packages, API packages |
| 실행환경 예제 다운로드 | `https://www.egovframe.go.kr/home/sub.do?menuNo=37` | Boot starter examples, AI/RAG examples, cloud stream examples |
| 개발환경 다운로드 | `https://www.egovframe.go.kr/home/sub.do?menuNo=107` | developer IDE bundles, Eclipse plugin binaries, plugin source ZIPs, patch ZIPs |
| 운영환경 다운로드 | `https://www.egovframe.go.kr/home/sub.do?menuNo=46` | BOPR, MSA operating environment, CMS packages |
| 공통컴포넌트 다운로드 | `https://www.egovframe.go.kr/home/sub.do?menuNo=49` | common component templates, all-in-one packages, MSA common components |
| 공통컴포넌트 분류별 다운로드 | `https://www.egovframe.go.kr/home/sub.do?menuNo=91` | large component catalog; list count is captured but full detail fan-out is intentionally skipped |
| 모바일 다운로드 | `https://www.egovframe.go.kr/home/sub.do?menuNo=101`, `102`, `105` | device API app/server and mobile common component packages |

## How To Answer ZIP Questions

For questions like "이 ZIP도 대응하나?", answer in three levels:

1. **Metadata covered:** The plugin can find captured filename, page URL, attachment URL when available, size text, release text, and checksum text.
2. **Internal structure not assumed:** Do not claim package contents, project structure, dependencies, or scripts unless the ZIP has been downloaded and inspected for the current task.
3. **Live freshness needed:** If the user asks for "latest" or a specific current download package, check the live portal page because portal ZIP lists can change.

## Safe ZIP Handling

When the user explicitly asks to download or inspect a ZIP:

1. Download from the official portal URL only.
2. Save to a temporary or user-approved workspace path.
3. Verify MD5, SHA1, or SHA256 if the portal page provides it.
4. Inspect the archive listing before extraction.
5. Extract only into a temporary/sandbox directory.
6. Do not execute bundled scripts, installers, or binaries automatically.
7. Summarize project type from files such as `pom.xml`, `build.gradle`, `settings.gradle`, `package.json`, `Dockerfile`, `application.properties`, `application.yml`, mapper XML, JSP, and SQL scripts.

## Known Limitation

The bundle is good at download metadata coverage. It is not a mirror of the eGovFrame binary download center, and it does not store ZIP internals. For exact internal contents, inspect the specific archive on demand.
