package org.example.egov.board.service;

import java.time.LocalDateTime;

public record BoardPostResponse(
        long postId,
        String title,
        LocalDateTime createdAt
) {
}
