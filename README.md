<p align="right">
  <a href="README.en.md">English</a> | <strong>한국어</strong>
</p>

# eGovFrame Guardian

<p align="center">
  <img src="assets/egovframe-guardian-mascot-retro.png" alt="eGovFrame Guardian 레트로 도트 마스코트" width="180">
</p>

<p align="center">
  <a href="https://github.com/unnest-wintenboy/egovframe-guardian/releases"><img alt="GitHub release" src="https://img.shields.io/github/v/release/unnest-wintenboy/egovframe-guardian?label=release"></a>
  <a href="LICENSE"><img alt="License: MIT" src="https://img.shields.io/badge/license-MIT-green.svg"></a>
  <img alt="Codex plugin" src="https://img.shields.io/badge/Codex-plugin-0f172a">
  <img alt="Claude Code plugin" src="https://img.shields.io/badge/Claude%20Code-plugin-5b21b6">
</p>

<p align="center">
  <strong>한국 전자정부 표준프레임워크 프로젝트를 위한 다정한 에이전트 가드레일 키트.</strong>
  <br>
  Codex와 Claude Code에서 eGovFrame 기준에 맞게 만들고, 검토하고, 스캔합니다.
</p>

eGovFrame Guardian은 코딩 에이전트가 자주 놓치는 맥락을 가까이에 둡니다. 공식 eGovFrame 포털 요약, GitHub 저장소 인덱스, 바로 참고할 수 있는 Java 예제, 그리고 프레임워크 관례에서 벗어난 부분을 조기에 잡아주는 로컬 hook을 함께 제공합니다.

classic MVC, eGovFrame Boot, MyBatis, Spring Security, batch, MSA, 호환성 확인, 공공 Java 시스템 유지보수 작업에 쓰기 좋습니다.

## 왜 만들었나요

eGovFrame 프로젝트는 조용한 부분에서 자주 흔들립니다. mapper namespace, transaction boundary, runtime metadata, controller 안으로 새어 들어온 SQL, 현재 표준과 맞지 않는 예제 복붙 같은 문제들입니다. 이 플러그인은 에이전트가 코드를 수정하고 검토하고 유지보수하는 동안 그런 세부 기준을 계속 곁에 둡니다.

좋은 의미로 지루하게 만들었습니다. 데이터 기반 규칙, 재현 가능한 검사, 공식 eGovFrame 포털과 GitHub 조직으로 이어지는 출처를 기본으로 둡니다.

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

| 이름 | 쉽게 말하면 | 언제 쓰나요 |
| --- | --- | --- |
| `egovframe-developer` skill | 에이전트가 표준프레임워크 방식으로 일하도록 돕는 작업 설명서 | 코드 작성, 리뷰, 마이그레이션, 호환성 확인을 맡길 때 |
| 포털 기반 reference | 공식 eGovFrame 내용을 읽기 쉽게 정리한 참고 자료 | 에이전트가 일반 Spring 방식으로만 답하지 않게 하고 싶을 때 |
| 예제 코드 | 바로 따라 볼 수 있는 MVC, Boot REST, MyBatis, security, batch, MSA 예제 | 새 기능의 기본 모양을 잡을 때 |
| ZIP 다운로드와 배포파일 사용 | 포털 ZIP 파일명, 페이지 URL, 첨부 URL, 크기, checksum을 찾고 받은 ZIP을 풀기 전에 검사 | 표준프레임워크 사이트의 배포파일을 프로젝트에 적용할 때 |
| hook guardrail | 사용자가 직접 부르지 않아도 자동으로 켜지는 안전장치 | 위험한 명령을 막거나, 파일 수정 뒤 문제를 바로 찾을 때 |
| scanner | 흔한 eGovFrame 실수를 찾는 검사기 | controller SQL, mapper namespace, transaction 누락 등을 확인할 때 |

## Skill은 이렇게 씁니다

Skill은 별도의 앱 버튼이 아니라, 에이전트에게 “이 기준으로 일해줘”라고 알려주는 작업 모드입니다. 플러그인을 켠 뒤 프롬프트에 `eGovFrame Guardian` 또는 `egovframe-developer`를 말하면 됩니다.

좋은 요청은 짧고 구체적이면 됩니다.

```text
Use eGovFrame Guardian to review this service and mapper layout.
```

```text
eGovFrame Guardian 기준으로 Boot REST CRUD 예제를 MyBatis로 만들어줘.
```

```text
이 프로젝트가 eGovFrame transaction, mapper, runtime metadata 관례를 지키는지 확인해줘.
```

```text
이 controller/service/mapper 흐름을 현재 표준프레임워크 스타일로 정리해줘.
```

에이전트는 이 skill을 읽고 공식 포털 요약, repo index, 예제 코드, scanner 규칙을 함께 참고합니다. 가능하면 작업 목적, 확인할 폴더, 사용 중인 eGovFrame 버전, classic MVC인지 Boot인지도 같이 알려주세요.

## Hook은 언제, 왜 발동되나요

Hook은 사용자가 직접 실행하는 명령이 아닙니다. Codex나 Claude Code가 작업 흐름 중 특정 순간에 자동으로 부르는 작은 안전장치입니다. 목적은 에이전트가 eGovFrame 기준을 잊지 않게 하고, 위험한 작업을 하기 전에 한 번 더 멈추게 하는 것입니다.

| 언제 발동되나요 | 왜 필요한가요 | 무슨 일이 일어나나요 |
| --- | --- | --- |
| 세션이 시작될 때 `SessionStart` | 플러그인이 켜져 있다는 사실을 에이전트가 바로 알아야 합니다 | eGovFrame skill과 guardrail이 준비됐다고 알려줍니다 |
| 프롬프트를 보낼 때 `UserPromptSubmit` | 사용자가 eGovFrame, egovframework, 표준프레임워크 같은 신호를 주면 표준프레임워크 맥락이 필요합니다 | 공식 포털 기반 맥락을 프롬프트에 더해 일반 Spring 답변으로 흐르지 않게 합니다 |
| 도구를 쓰기 직전 `PreToolUse` | 삭제, 이동, 덮어쓰기 같은 명령은 실수하면 복구가 어렵습니다 | eGovFrame 또는 플러그인 핵심 경로를 건드리는 destructive command를 막습니다 |
| 권한 요청이 날 때 `PermissionRequest` | 위험한 명령은 승인 전에 한 번 더 걸러야 합니다 | 보호 경로에 대한 destructive approval request를 거부합니다 |
| 파일을 고친 직후 `PostToolUse` | 문제는 코드를 쓴 뒤 바로 보는 것이 가장 싸게 고칠 수 있습니다 | scanner를 돌려 controller SQL, mapper, transaction, secret 같은 문제를 찾습니다 |
| subagent가 시작될 때 `SubagentStart` | eGovFrame 작업을 맡은 다른 에이전트도 같은 기준으로 일해야 합니다 | subagent 요청에 eGovFrame 신호가 있을 때만 맥락을 전달합니다 |
| subagent가 끝나려 할 때 `SubagentStop` | 이미 발견된 문제가 남았는데 끝내면 놓치기 쉽습니다 | 현재 프로젝트의 추적 중인 blocking finding이 있을 때만 종료를 막습니다 |
| 대화가 압축된 뒤 `PostCompact` | 긴 작업 중 압축이 되면 중요한 기준이 빠질 수 있습니다 | eGovFrame guard context를 다시 복원합니다 |
| 턴을 끝내기 직전 `Stop` | 이전 hook에서 기록한 blocking finding이 남았는지 확인해야 합니다 | 현재 프로젝트에 기록된 문제가 있을 때만 에이전트가 한 번 더 계속 작업하게 합니다 |

위험한 shell command를 정말 실행해야 한다면 command에 `egovframe-guardian:allow-destructive`를 명시해야 합니다. 이 token은 실수로 삭제성 명령이 통과하지 않게 만드는 확인 장치입니다.

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

## 배포 ZIP 검사

표준프레임워크 사이트에서 ZIP을 받았다면 바로 풀지 말고 먼저 검사하세요.

```bash
python scripts/egovframe_distribution.py inspect --zip path/to/package.zip --expected-sha1 <portal-sha1> --json
```

이 검사는 checksum 일치 여부, ZIP-slip 위험 경로, 실행 파일/스크립트 포함 여부, Maven/Gradle/Spring/MyBatis/JSP/SQL 신호, 배포파일 유형을 알려줍니다. 소스 프로젝트 ZIP은 임시 폴더에 푼 뒤 필요한 controller, service, mapper, config, SQL만 선별해서 적용하는 흐름을 권장합니다.

포털 크롤에 잡힌 ZIP 범위를 요약하려면:

```bash
python scripts/egovframe_distribution.py inventory --portal-json skills/egovframe-developer/references/portal-crawl-records.json --json
```

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

## 개발자 문서

플러그인을 수정하거나 배포하려는 관리자는 [development notes](docs/development.md)를 보세요. 일반 사용자는 위 설치와 사용 방법만 알면 됩니다.

## 출처

이 플러그인은 다음 자료를 바탕으로 만든 요약, 인덱스, 예제를 포함합니다.

- eGovFrame portal: <https://www.egovframe.go.kr/home/main.do>
- eGovFrame GitHub organization: <https://github.com/egovframework>

Bundled crawl record와 repository atlas는 개발 가이드를 위한 자료입니다. 원본 upstream project 자료는 각 출처의 조건을 따릅니다.

## 라이선스

이 저장소의 코드, 문서, 생성된 마스코트 asset은 [MIT License](LICENSE)로 배포됩니다. 이 플러그인이 참고하거나 요약한 upstream eGovFrame 자료는 각 원 출처의 조건을 따릅니다.

## 한계

eGovFrame Guardian은 개발 보조 도구입니다. 공식 eGovFrame 문서, 프로젝트별 architecture review, security review, compatibility testing을 대체하지 않습니다. Static check는 false positive와 false negative를 만들 수 있습니다.
