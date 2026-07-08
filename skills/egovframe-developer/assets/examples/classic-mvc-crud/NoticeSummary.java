package org.example.egov.notice.service;

import java.time.LocalDateTime;

public record NoticeSummary(
        long noticeId,
        String title,
        LocalDateTime createdAt
) {
}
