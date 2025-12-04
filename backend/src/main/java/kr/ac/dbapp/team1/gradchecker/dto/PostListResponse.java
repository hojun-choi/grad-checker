// src/main/java/kr/ac/dbapp/team1/gradchecker/dto/PostListResponse.java
package kr.ac.dbapp.team1.gradchecker.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import org.springframework.data.domain.Page;

import java.util.List;

@Getter
@AllArgsConstructor
public class PostListResponse {

    @Getter
    @Builder
    public static class PostPage {
        private List<PostResponse> content;
        private long totalElements;
        private int totalPages;
        private int page;
        private int size;
    }

    private PostPage posts;
    private List<BoardTypeResponse> boardTypes;

    public static PostListResponse of(Page<PostResponse> page,
                                      List<BoardTypeResponse> boardTypes) {
        PostPage postPage = PostPage.builder()
                .content(page.getContent())
                .totalElements(page.getTotalElements())
                .totalPages(page.getTotalPages())
                .page(page.getNumber())
                .size(page.getSize())
                .build();

        return new PostListResponse(postPage, boardTypes);
    }
}
