from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Literal, TypeAlias


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
GUARD = PLUGIN_ROOT / "scripts" / "egovframe_guard.py"
SampleKind: TypeAlias = Literal["classic-mvc", "boot-rest", "msa-service", "batch-job"]
SAMPLE_KINDS: tuple[SampleKind, ...] = ("classic-mvc", "boot-rest", "msa-service", "batch-job")


def write_file(root: Path, relative: str, body: str) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    _ = path.write_text(body, encoding="utf-8")


def write_build(root: Path) -> None:
    write_file(
        root,
        "pom.xml",
        "<project><dependencies><dependency><groupId>org.egovframe.rte</groupId></dependency></dependencies></project>",
    )


def write_classic_mvc(root: Path) -> None:
    write_build(root)
    write_file(
        root,
        "src/main/java/egovframework/demo/web/NoticeController.java",
        "package egovframework.demo.web; public class NoticeController { public String list() { return \"notice/list\"; } }",
    )
    write_file(
        root,
        "src/main/java/egovframework/demo/config/MapperConfig.java",
        "package egovframework.demo.config; import org.mybatis.spring.annotation.MapperScan; @MapperScan(\"egovframework.demo\") public class MapperConfig {}",
    )
    write_file(
        root,
        "src/main/resources/egovframework/sqlmap/NoticeMapper.xml",
        "<!DOCTYPE mapper><mapper namespace=\"egovframework.demo.NoticeMapper\"></mapper>",
    )


def write_boot_rest(root: Path) -> None:
    write_build(root)
    write_file(
        root,
        "src/main/java/egovframework/demo/api/NoticeRestController.java",
        "package egovframework.demo.api; public class NoticeRestController { public String list() { return \"ok\"; } }",
    )
    write_file(
        root,
        "src/main/java/egovframework/demo/service/NoticeServiceImpl.java",
        "package egovframework.demo.service; import org.springframework.transaction.annotation.Transactional; public class NoticeServiceImpl { @Transactional public void saveNotice() {} }",
    )
    write_file(
        root,
        "src/main/resources/application.yml",
        "spring:\n  datasource:\n    password: ${DB_PASSWORD}\nmybatis:\n  mapper-locations: classpath:/egovframework/sqlmap/*.xml\n",
    )
    write_file(
        root,
        "src/main/resources/egovframework/sqlmap/NoticeMapper.xml",
        "<!DOCTYPE mapper><mapper namespace=\"egovframework.demo.NoticeMapper\"></mapper>",
    )


def write_msa_service(root: Path) -> None:
    write_build(root)
    write_file(
        root,
        "src/main/java/egovframework/msa/board/BoardApplication.java",
        "package egovframework.msa.board; public class BoardApplication { public static void main(String[] args) {} }",
    )
    write_file(
        root,
        "src/main/resources/application.yml",
        "spring:\n  application:\n    name: board-service\nserver:\n  port: ${SERVER_PORT:8080}\n",
    )


def write_batch_job(root: Path) -> None:
    write_build(root)
    write_file(
        root,
        "src/main/java/egovframework/batch/notice/NoticeArchiveTasklet.java",
        "package egovframework.batch.notice; public class NoticeArchiveTasklet { public void archive() {} }",
    )
    write_file(
        root,
        "src/main/resources/egovframework/batch/notice-archive-job.xml",
        "<beans><bean id=\"noticeArchiveTasklet\" class=\"egovframework.batch.notice.NoticeArchiveTasklet\" /></beans>",
    )


def make_sample(root: Path, kind: SampleKind) -> None:
    match kind:
        case "classic-mvc":
            write_classic_mvc(root)
        case "boot-rest":
            write_boot_rest(root)
        case "msa-service":
            write_msa_service(root)
        case "batch-job":
            write_batch_job(root)


def test_egovframe_sample_matrix_scans_without_blocking_findings(tmp_path: Path) -> None:
    for kind in SAMPLE_KINDS:
        project = tmp_path / kind
        make_sample(project, kind)
        result = subprocess.run(
            [sys.executable, str(GUARD), "--mode", "scan", "--root", str(project)],
            text=True,
            capture_output=True,
            check=False,
        )
        assert result.returncode == 0
        assert "errors=0" in result.stdout
        assert "no eGovFrame project signals" not in result.stdout
