# Example Code Catalog

Use these assets as small, original starter patterns. They are not copied from upstream repositories; adapt them to the target project after inspecting the official examples.

## `assets/examples/classic-mvc-crud`

Classic JSP/Spring MVC/MyBatis shape:

- `NoticeController.java`
- `NoticeService.java`
- `NoticeServiceImpl.java`
- `NoticeMapper.java`
- `NoticeMapper.xml`
- `notice-list.jsp`

Use when adding a CRUD screen to a classic eGovFrame web app.

## `assets/examples/boot-rest-crud`

Boot REST/MyBatis shape:

- `NoticeRestController.java`
- `NoticeCreateRequest.java`
- `NoticeResponse.java`
- `NoticeService.java`
- `NoticeMapper.java`
- `NoticeMapper.xml`
- `application-notice.properties`

Use when building REST APIs in Boot templates or Java-config samples.

## `assets/examples/msa-service`

MSA service shape:

- `BoardApplication.java`
- `BoardApi.java`
- `BoardCommandService.java`
- `application.yml`
- `Dockerfile`
- `k8s-deployment.yml`

Use when adding or splitting a service in an eGovFrame MSA environment.

## `assets/examples/batch-job`

Batch job shape:

- `NoticeArchiveJobConfig.java`
- `NoticeArchiveTasklet.java`
- `notice-archive-job.xml`

Use when adding a scheduled/archive/batch process.

## `assets/examples/security-login`

Security/login integration shape:

- `LoginController.java`
- `LoginRequest.java`
- `LoginService.java`
- `SecurityConfig.java`

Use when wiring login, authorization checks, or session-based security.

## `assets/examples/react-client`

React client integration shape:

- `egovApi.js`
- `NoticeList.jsx`
- `noticeRoutes.js`

Use when connecting the official React template style to a Boot backend.

## Adaptation Rules

- Keep examples small; copy only the files needed for the requested change.
- Replace `org.example.egov` package names.
- Replace `NOTICE` table/mapper names with project names.
- Replace DTO validation annotations with the target’s validation policy.
- Replace datasource, discovery, and gateway settings with environment variables or project config.
- Add tests after adaptation; examples are skeletons, not verified project code.
