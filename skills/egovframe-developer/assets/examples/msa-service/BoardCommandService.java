package org.example.egov.board.service;

import java.util.List;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class BoardCommandService {
    private final BoardPostMapper boardPostMapper;

    public BoardCommandService(BoardPostMapper boardPostMapper) {
        this.boardPostMapper = boardPostMapper;
    }

    @Transactional(readOnly = true)
    public List<BoardPostResponse> findRecentPosts() {
        return boardPostMapper.selectRecentPosts();
    }
}
