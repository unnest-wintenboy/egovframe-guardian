package org.example.egov.board.api;

import java.util.List;
import org.example.egov.board.service.BoardCommandService;
import org.example.egov.board.service.BoardPostResponse;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/boards")
public class BoardApi {
    private final BoardCommandService boardCommandService;

    public BoardApi(BoardCommandService boardCommandService) {
        this.boardCommandService = boardCommandService;
    }

    @GetMapping("/posts")
    public List<BoardPostResponse> posts() {
        return boardCommandService.findRecentPosts();
    }
}
