package org.example.egov.notice.api;

import jakarta.validation.Valid;
import java.net.URI;
import java.util.List;
import org.example.egov.notice.service.NoticeResponse;
import org.example.egov.notice.service.NoticeService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/notices")
public class NoticeRestController {
    private final NoticeService noticeService;

    public NoticeRestController(NoticeService noticeService) {
        this.noticeService = noticeService;
    }

    @GetMapping
    public List<NoticeResponse> list() {
        return noticeService.findNotices();
    }

    @PostMapping
    public ResponseEntity<NoticeResponse> create(@Valid @RequestBody NoticeCreateRequest request) {
        NoticeResponse created = noticeService.createNotice(request.toCommand());
        return ResponseEntity.created(URI.create("/api/notices/" + created.noticeId())).body(created);
    }
}
