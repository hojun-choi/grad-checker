// src/main/java/kr/ac/dbapp/team1/gradchecker/dto/PostResponse.java
package kr.ac.dbapp.team1.gradchecker.dto;

import kr.ac.dbapp.team1.gradchecker.domain.Post;
import lombok.Builder;
import lombok.Getter;

import java.util.List;

@Getter
@Builder
public class PostResponse {

    private Long id;
    private String category;    // 게시판명 (board_name)
    private String title;
    private String content;
    private String author;
    private boolean anonymous;
    private String createdAt;
    private int views;
    private int replies;

    // 상세 화면에서 사용할 댓글 목록
    private List<CommentResponse> comments;

    public static PostResponse from(Post post) {
        return PostResponse.builder()
                .id(post.getId())
                .category(post.getBoardType().getBoardName())
                .title(post.getTitle())
                .content(post.getContent())
                .author(post.getUser().getUsername())
                .anonymous(Boolean.TRUE.equals(post.getIsAnonymous()))
                .createdAt(post.getCreatedAt().toString())
                .views(post.getViewCount())
                .replies(post.getCommentCount())
                .build();
    }

    public static PostResponse from(Post post, List<CommentResponse> comments) {
        return PostResponse.builder()
                .id(post.getId())
                .category(post.getBoardType().getBoardName())
                .title(post.getTitle())
                .content(post.getContent())
                .author(post.getUser().getUsername())
                .anonymous(Boolean.TRUE.equals(post.getIsAnonymous()))
                .createdAt(post.getCreatedAt().toString())
                .views(post.getViewCount())
                .replies(post.getCommentCount())
                .comments(comments)
                .build();
    }
}
