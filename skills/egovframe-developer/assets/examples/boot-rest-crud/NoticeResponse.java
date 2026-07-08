package org.example.egov.notice.service;

import java.time.LocalDateTime;

public record NoticeResponse(
        long noticeId,
        String title,
        String contents,
        LocalDateTime createdAt
) {
}
