package org.example.egov.notice.web;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import org.example.egov.notice.service.CreateNoticeCommand;

public class NoticeForm {
    @NotBlank
    @Size(max = 200)
    private String title;

    @NotBlank
    private String contents;

    public CreateNoticeCommand toCommand() {
        return new CreateNoticeCommand(0L, title, contents, "system");
    }

    public String getTitle() {
        return title;
    }

    public void setTitle(String title) {
        this.title = title;
    }

    public String getContents() {
        return contents;
    }

    public void setContents(String contents) {
        this.contents = contents;
    }
}
