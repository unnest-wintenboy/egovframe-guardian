package org.example.egov.notice.service.impl;

import java.util.List;
import org.apache.ibatis.annotations.Mapper;
import org.example.egov.notice.service.CreateNoticeCommand;
import org.example.egov.notice.service.NoticeSearchCondition;
import org.example.egov.notice.service.NoticeSummary;

@Mapper
public interface NoticeMapper {
    List<NoticeSummary> selectNotices(NoticeSearchCondition condition);

    int insertNotice(CreateNoticeCommand command);
}
