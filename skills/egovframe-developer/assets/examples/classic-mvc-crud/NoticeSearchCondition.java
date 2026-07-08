package org.example.egov.notice.service;

public record NoticeSearchCondition(
        String keyword,
        int pageIndex,
        int pageUnit
) {
}
