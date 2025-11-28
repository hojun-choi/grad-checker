package kr.ac.dbapp.team1.gradchecker.dto;

import lombok.Builder;
import lombok.Getter;
import org.springframework.data.domain.Page;

import java.util.List;

@Getter
@Builder
public class PostListResponse {
    private Page<PostResponse> posts;
    private List<BoardTypeResponse> boardTypes;

    public static PostListResponse of(Page<PostResponse> posts, List<BoardTypeResponse> boardTypes) {
        return PostListResponse.builder()
                .posts(posts)
                .boardTypes(boardTypes)
                .build();
    }
}
