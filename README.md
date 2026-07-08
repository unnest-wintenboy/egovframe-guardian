<p align="right">
  <a href="README.en.md">English</a> | <strong>한국어</strong>
</p>

# eGovFrame Guardian

<p align="center">
  <img src="assets/egovframe-guardian-mascot.png" alt="eGovFrame Guardian 마스코트" width="180">
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
  <strong>한국 전자정부 표준프레임워크 프로젝트를 위한 다정한 에이전트 가드레일 키트.</strong>
  <br>
  Codex와 Claude Code에서 eGovFrame 기준에 맞게 만들고, 검토하고, 스캔하고, 배포합니다.
</p>

eGovFrame Guardian은 코딩 에이전트가 자주 놓치는 맥락을 가까이에 둡니다. 공식 eGovFrame 포털 요약, GitHub 저장소 인덱스, 바로 참고할 수 있는 Java 예제, 그리고 프레임워크 관례에서 벗어난 부분을 조기에 잡아주는 로컬 hook을 함께 제공합니다.

classic MVC, eGovFrame Boot, MyBatis, Spring Security, batch, MSA, 호환성 확인, 공공 Java 시스템 유지보수 작업에 쓰기 좋습니다.

## 왜 만들었나요

eGovFrame 프로젝트는 조용한 부분에서 자주 흔들립니다. mapper namespace, transaction boundary, runtime metadata, controller 안으로 새어 들어온 SQL, 현재 표준과 맞지 않는 예제 복붙 같은 문제들입니다. 이 플러그인은 에이전트가 코드를 수정하고 검토하고 릴리즈를 준비하는 동안 그런 세부 기준을 계속 곁에 둡니다.

좋은 의미로 지루하게 만들었습니다. 데이터 기반 규칙, 재현 가능한 검증, CI gate, 릴리즈 checksum, 공식 eGovFrame 포털과 GitHub 조직으로 이어지는 출처를 기본으로 둡니다.

## 빠른 시작

마켓플레이스를 추가하고 플러그인을 활성화한 뒤, 에이전트에게 `eGovFrame Guardian`을 사용하라고 요청하세요.

### Codex

```bash
codex plugin marketplace add unnest-wintenboy/egovframe-guardian
```

Codex plugin directory에서 **eGovFrame Guardian**을 선택하고, hook 정의를 검토한 뒤 활성화합니다.

### Claude Code

```text
/plugin marketplace add unnest-wintenboy/egovframe-guardian
/plugin install egovframe-guardian@egovframe-guardian
```

로컬에서 플러그인을 테스트하려면:

```bash
claude --plugin-dir .
```

플러그인 hook은 로컬에서 실행됩니다. Codex나 Claude Code에서 활성화하기 전에 hook 정의를 검토하고 신뢰할 수 있는지 확인하세요.

## 무엇이 들어있나요

| 필요 | 포함된 것 |
| --- | --- |
| 표준에 맞춰 개발 | classic MVC, Boot REST, MyBatis, security, batch, MSA, compatibility, source refresh 작업을 돕는 `egovframe-developer` skill |
| 에이전트 맥락 보강 | 표준프레임워크 소개, 개발 가이드, 다운로드, 개발자 참여, 기술 지원, 호환성 확인, v5.0.0 하이라이트를 반영한 포털 기반 reference |
| 바로 시작할 예제 | MVC CRUD, Boot REST CRUD, login/security, batch job, MSA service structure, React client integration 예제 |
| 어긋남 조기 감지 | controller SQL leakage, 누락된 mapper namespace, literal secret, transaction 누락, mapper discovery gap, eGovFrame runtime metadata 누락을 잡는 guard scanner |
| 믿고 배포 | validation, tests, coverage, maturity scoring, package checks, archives, checksums, GitHub Releases를 담당하는 GitHub Actions |

## 이렇게 써보세요

```text
Use eGovFrame Guardian to review this service and mapper layout.
```

```text
Use eGovFrame Guardian to build an eGovFrame Boot REST CRUD example with MyBatis.
```

```text
Use eGovFrame Guardian to check whether this project follows eGovFrame transaction and mapper conventions.
```

```text
Use eGovFrame Guardian to migrate this controller/service/mapper flow toward the current standard.
```

## 가드레일

플러그인은 Codex와 Claude 호환 plugin 환경에서 동작하는 lifecycle hook을 `hooks/hooks.json`에 설치합니다.

| Hook | 역할 |
| --- | --- |
| `SessionStart` | eGovFrame skill과 guardrail이 준비되었음을 알립니다 |
| `UserPromptSubmit` | framework, runtime, MyBatis, compatibility, AI RAG, VS Code, Istio, OpenTelemetry, Flutter device APIs 등 관련 prompt에 eGovFrame 맥락을 추가합니다 |
| `PreToolUse` | 명시적으로 허용되지 않은 eGovFrame 또는 plugin 핵심 경로 대상 destructive command를 차단합니다 |
| `PermissionRequest` | 보호 경로에 대한 destructive approval request를 거부합니다 |
| `PostToolUse` | edit/write tool 이후 guard scanner를 실행합니다 |
| `SubagentStart` | subagent에도 같은 포털 기반 eGovFrame 맥락을 제공합니다 |
| `SubagentStop` | 추적 중인 eGovFrame finding이 남아 있으면 subagent가 종료하지 못하게 합니다 |
| `PostCompact` | conversation compaction 이후 guard context를 복원합니다 |
| `Stop` | 에이전트가 턴을 끝내기 전에 추적 중인 finding을 확인하고, 필요하면 한 번 더 계속 작업하게 합니다 |

Destructive shell command를 허용하려면 명시적인 token `egovframe-guardian:allow-destructive`가 command에 포함되어야 합니다.

## 스캐너 규칙

직접 스캔하려면:

```bash
python scripts/egovframe_guard.py --mode scan --root .
```

현재 확인하는 항목:

- controller 내부 inline SQL 또는 직접 `JdbcTemplate` / `SqlSession` 접근
- `namespace`가 없는 MyBatis mapper XML
- config 파일의 literal secret 의심 값
- transaction boundary가 없는 write-oriented service implementation
- mapper discovery configuration 없이 존재하는 mapper XML
- 명시적인 eGovFrame runtime dependency metadata가 없는 eGovFrame 프로젝트

직접 scan mode에서는 high-confidence error가 exit code `2`를 반환하고, warning은 exit code `0`을 반환합니다. Hook mode에서는 host가 context를 추가하거나, 지원되는 tool call을 거부하거나, hook contract에 따라 턴을 계속할 수 있도록 structured hook JSON을 반환합니다.

## 설정

기본 scanner policy:

```text
config/egovframe-guardian.json
```

프로젝트별 noisy rule override:

```text
.egovframe-guardian.json
```

Rule severity와 suppression은 데이터 기반이므로 scanner code를 수정하지 않고 팀별로 조정할 수 있습니다.

## 로컬 검증

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

Claude Code가 설치되어 있다면:

```bash
claude plugin validate .
```

Codex plugin creator tooling이 설치되어 있다면:

```bash
python ~/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py .
```

## 릴리즈 흐름

Pull request와 push는 JSON validation, Python compile check, strict `basedpyright`, bundled skill validation, reference coverage audit, pytest, coverage, maturity scoring, public release metadata validation을 실행합니다.

Semantic version tag로 릴리즈합니다.

```bash
git tag vX.Y.Z
git push origin vX.Y.Z
```

Release workflow는 `.zip`과 `.tar.gz` archive를 만들고, SHA-256 checksum을 출력하고, GitHub Release를 생성합니다.

## 저장소 지도

```text
README.md                             한국어 기본 README
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

## 출처

이 플러그인은 다음 자료를 바탕으로 만든 요약, 인덱스, 예제를 포함합니다.

- eGovFrame portal: <https://www.egovframe.go.kr/home/main.do>
- eGovFrame GitHub organization: <https://github.com/egovframework>

Bundled crawl record와 repository atlas는 개발 가이드를 위한 자료입니다. 원본 upstream project 자료는 각 출처의 조건을 따릅니다.

## 현재 배포 메모

공식 Codex Plugin Directory의 self-serve publishing은 아직 일반 공개되어 있지 않아, 이 저장소는 public self-hosted Codex marketplace catalog를 제공합니다. Claude Code community marketplace submission은 로컬 검증 이후 Anthropic review가 필요합니다.

## 한계

eGovFrame Guardian은 개발 보조 도구입니다. 공식 eGovFrame 문서, 프로젝트별 architecture review, security review, compatibility testing을 대체하지 않습니다. Static check는 false positive와 false negative를 만들 수 있습니다.
