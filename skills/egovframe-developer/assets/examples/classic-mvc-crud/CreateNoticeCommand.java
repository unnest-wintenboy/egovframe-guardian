package org.example.egov.notice.service;

public record CreateNoticeCommand(
        long noticeId,
        String title,
        String contents,
        String createdBy
) {
}
