package org.example.egov.notice.service.impl;

import java.util.List;
import org.example.egov.notice.service.CreateNoticeCommand;
import org.example.egov.notice.service.NoticeSearchCondition;
import org.example.egov.notice.service.NoticeService;
import org.example.egov.notice.service.NoticeSummary;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class NoticeServiceImpl implements NoticeService {
    private final NoticeMapper noticeMapper;

    public NoticeServiceImpl(NoticeMapper noticeMapper) {
        this.noticeMapper = noticeMapper;
    }

    @Override
    @Transactional(readOnly = true)
    public List<NoticeSummary> findNotices(NoticeSearchCondition condition) {
        return noticeMapper.selectNotices(condition);
    }

    @Override
    @Transactional
    public long createNotice(CreateNoticeCommand command) {
        noticeMapper.insertNotice(command);
        return command.noticeId();
    }
}
