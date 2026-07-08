package org.example.egov.notice.web;

import jakarta.validation.Valid;
import org.example.egov.notice.service.NoticeSearchCondition;
import org.example.egov.notice.service.NoticeService;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.validation.BindingResult;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.ModelAttribute;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;

@Controller
@RequestMapping("/notice")
public class NoticeController {
    private final NoticeService noticeService;

    public NoticeController(NoticeService noticeService) {
        this.noticeService = noticeService;
    }

    @GetMapping
    public String list(@ModelAttribute NoticeSearchCondition condition, Model model) {
        model.addAttribute("notices", noticeService.findNotices(condition));
        return "notice/notice-list";
    }

    @PostMapping
    public String create(@Valid NoticeForm form, BindingResult bindingResult) {
        if (bindingResult.hasErrors()) {
            return "notice/notice-form";
        }
        noticeService.createNotice(form.toCommand());
        return "redirect:/notice";
    }
}
