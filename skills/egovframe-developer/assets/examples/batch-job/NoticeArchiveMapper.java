package org.example.egov.batch;

import org.apache.ibatis.annotations.Mapper;

@Mapper
public interface NoticeArchiveMapper {
    int archiveExpiredNotices();
}
