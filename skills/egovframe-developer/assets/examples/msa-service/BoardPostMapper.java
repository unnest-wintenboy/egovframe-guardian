package org.example.egov.board.service;

import java.util.List;
import org.apache.ibatis.annotations.Mapper;

@Mapper
public interface BoardPostMapper {
    List<BoardPostResponse> selectRecentPosts();
}
