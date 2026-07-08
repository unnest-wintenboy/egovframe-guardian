package org.example.egov.batch;

import org.springframework.batch.core.Job;
import org.springframework.batch.core.Step;
import org.springframework.batch.core.job.builder.JobBuilder;
import org.springframework.batch.core.repository.JobRepository;
import org.springframework.batch.core.step.builder.StepBuilder;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.transaction.PlatformTransactionManager;

@Configuration
public class NoticeArchiveJobConfig {
    @Bean
    public Job noticeArchiveJob(JobRepository jobRepository, Step noticeArchiveStep) {
        return new JobBuilder("noticeArchiveJob", jobRepository)
                .start(noticeArchiveStep)
                .build();
    }

    @Bean
    public Step noticeArchiveStep(
            JobRepository jobRepository,
            PlatformTransactionManager transactionManager,
            NoticeArchiveTasklet tasklet
    ) {
        return new StepBuilder("noticeArchiveStep", jobRepository)
                .tasklet(tasklet, transactionManager)
                .build();
    }
}
