package org.example.egov.notice.service;

import java.util.List;
import org.apache.ibatis.annotations.Mapper;

@Mapper
public interface NoticeMapper {
    List<NoticeResponse> selectNotices();

    NoticeResponse selectNotice(long noticeId);

    int insertNotice(CreateNoticeCommand command);
}
