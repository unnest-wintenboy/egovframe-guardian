package org.example.egov.notice.service;

public class CreateNoticeCommand {
    private Long noticeId;
    private final String title;
    private final String contents;

    public CreateNoticeCommand(String title, String contents) {
        this.title = title;
        this.contents = contents;
    }

    public Long getNoticeId() {
        return noticeId;
    }

    public void setNoticeId(Long noticeId) {
        this.noticeId = noticeId;
    }

    public String getTitle() {
        return title;
    }

    public String getContents() {
        return contents;
    }

    public long noticeId() {
        if (noticeId == null) {
            throw new IllegalStateException("noticeId has not been generated");
        }
        return noticeId;
    }
}
