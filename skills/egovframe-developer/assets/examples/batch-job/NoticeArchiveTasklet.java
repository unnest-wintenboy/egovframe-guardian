package org.example.egov.batch;

import org.springframework.batch.core.StepContribution;
import org.springframework.batch.core.scope.context.ChunkContext;
import org.springframework.batch.core.step.tasklet.Tasklet;
import org.springframework.batch.repeat.RepeatStatus;
import org.springframework.stereotype.Component;

@Component
public class NoticeArchiveTasklet implements Tasklet {
    private final NoticeArchiveMapper noticeArchiveMapper;

    public NoticeArchiveTasklet(NoticeArchiveMapper noticeArchiveMapper) {
        this.noticeArchiveMapper = noticeArchiveMapper;
    }

    @Override
    public RepeatStatus execute(StepContribution contribution, ChunkContext chunkContext) {
        int archived = noticeArchiveMapper.archiveExpiredNotices();
        contribution.incrementWriteCount(archived);
        return RepeatStatus.FINISHED;
    }
}
