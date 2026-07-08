package org.example.egov.notice.service;

import java.util.List;

public interface NoticeService {
    List<NoticeSummary> findNotices(NoticeSearchCondition condition);

    long createNotice(CreateNoticeCommand command);
}
