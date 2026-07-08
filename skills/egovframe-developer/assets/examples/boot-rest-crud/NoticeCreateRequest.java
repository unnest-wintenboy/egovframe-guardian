package org.example.egov.notice.api;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import org.example.egov.notice.service.CreateNoticeCommand;

public record NoticeCreateRequest(
        @NotBlank @Size(max = 200) String title,
        @NotBlank String contents
) {
    public CreateNoticeCommand toCommand() {
        return new CreateNoticeCommand(title, contents);
    }
}
