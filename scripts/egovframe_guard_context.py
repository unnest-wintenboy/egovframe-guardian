from __future__ import annotations

from typing import Final

CONFIRM_TOKEN: Final = "egovframe-guardian:allow-destructive"
PROMPT_MARKERS: Final = (
    "ai rag",
    "compatibility",
    "egovframe",
    "egovframework",
    "flutter",
    "istio",
    "mapper",
    "mybatis",
    "opentelemetry",
    "runtime",
    "vscode",
    "\uac1c\ubc1c\uac00\uc774\ub4dc",
    "\uac1c\ubc1c\ud658\uacbd",
    "\uacf5\ud1b5\ucef4\ud3ec\ub10c\ud2b8",
    "\uc2e4\ud589\ud658\uacbd",
    "\uc804\uc790\uc815\ubd80",
    "\ud45c\uc900\ud504\ub808\uc784\uc6cc\ud06c",
    "\ud638\ud658\uc131",
)
DESTRUCTIVE_MARKERS: Final = (
    "rm -rf",
    "rm -fr",
    "remove-item",
    "rmdir /s",
    "del /s",
    "git reset --hard",
    "git clean -fd",
    "git checkout --",
)
EGOV_CRITICAL_MARKERS: Final = (
    ".egovframe-guardian.json",
    "application.properties",
    "application.yml",
    "build.gradle",
    "dockerfile",
    "egovframework",
    "gatewayserver",
    "k8s",
    "mapper",
    "org.egovframe",
    "org/egovframe",
    "pom.xml",
    "settings.gradle",
    "src/main/java",
    "src/main/resources",
)
PLUGIN_CRITICAL_MARKERS: Final = (
    ".codex-plugin/plugin.json",
    ".codex-plugin\\plugin.json",
    "config/egovframe-guardian.json",
    "config\\egovframe-guardian.json",
    "hooks/hooks.json",
    "hooks\\hooks.json",
    "portal-crawl-records",
    "repository-directory",
    "scripts/egovframe_distribution.py",
    "scripts\\egovframe_distribution.py",
    "scripts/egovframe_guard.py",
    "scripts\\egovframe_guard.py",
    "skills/egovframe-developer",
    "skills\\egovframe-developer",
)
PROMPT_CONTEXT: Final = (
    "For eGovFrame work, load the bundled egovframe-developer skill context. Align with the "
    "official portal areas: introduction/architecture, development guide, downloads, developer "
    "participation, technical support, and compatibility confirmation. Current portal highlights "
    "include v5.0.0, VS Code Extension, AI RAG examples, Istio/OpenTelemetry operating guides, "
    "and Flutter device API programs. For portal ZIP distributions, verify checksums and inspect "
    "with scripts/egovframe_distribution.py before extraction. Prefer Controller-Service-Mapper "
    "layering and run the eGovFrame Guardian scan/Stop gate before claiming compliance."
)
COMPACT_CONTEXT: Final = (
    "eGovFrame Guardian: after compaction, reload the egovframe-developer skill before eGovFrame "
    "changes. Re-check the portal-aligned areas: runtime, development environment, operating "
    "environment, common components, mobile, support, compatibility confirmation, and distribution "
    "ZIP inspection workflow."
)
SUBAGENT_CONTEXT: Final = (
    "Subagent eGovFrame context: use egovframe-developer evidence first. The portal foregrounds "
    "v5.0.0, development guide/downloads, technical support, compatibility confirmation, VS Code "
    "Extension, AI RAG examples, Istio/OpenTelemetry operating guides, and Flutter device APIs. "
    "Inspect portal ZIP distributions before extraction. Do not finish without checking "
    "Controller-Service-Mapper layering and local guard findings."
)
