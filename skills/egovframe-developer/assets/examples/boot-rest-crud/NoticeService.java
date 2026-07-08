package org.example.egov.notice.service;

import java.util.List;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class NoticeService {
    private final NoticeMapper noticeMapper;

    public NoticeService(NoticeMapper noticeMapper) {
        this.noticeMapper = noticeMapper;
    }

    @Transactional(readOnly = true)
    public List<NoticeResponse> findNotices() {
        return noticeMapper.selectNotices();
    }

    @Transactional
    public NoticeResponse createNotice(CreateNoticeCommand command) {
        noticeMapper.insertNotice(command);
        return noticeMapper.selectNotice(command.noticeId());
    }
}
