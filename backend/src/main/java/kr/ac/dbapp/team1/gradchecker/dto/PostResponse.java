// src/main/java/kr/ac/dbapp/team1/gradchecker/dto/PostResponse.java
package kr.ac.dbapp.team1.gradchecker.dto;

import com.fasterxml.jackson.annotation.JsonProperty; // 추가
import kr.ac.dbapp.team1.gradchecker.domain.Post;
import lombok.Builder;
import lombok.Getter;

import java.util.List;

@Getter
@Builder
public class PostResponse {

    private Long id;
    private String category;
    private String title;
    private String content;
    private String author;

    // 응답 JSON 키는 계속 "isAnonymous" 사용
    @JsonProperty("isAnonymous")
    private boolean anonymous;

    private boolean isMine;
    private String createdAt;
    private int views;
    private int replies;
    private List<CommentResponse> comments;

    /**
     * 게시글 목록용 (댓글 없이)
     */
    public static PostResponse from(Post post, Long currentUserId) {
        return from(post, null, currentUserId);
    }

    /**
     * 게시글 상세용 (댓글 포함)
     */
    public static PostResponse from(Post post,
                                    List<CommentResponse> comments,
                                    Long currentUserId) {

        boolean isMine = currentUserId != null
                && post.getUser().getUserId().equals(currentUserId);

        boolean isAnonymous = Boolean.TRUE.equals(post.getIsAnonymous());

        // 🔽 author 표시 문자열 가공
        // 익명 X          -> 실제 작성자 이름
        // 익명 + 내 글    -> "나(익명)"
        // 익명 + 남의 글  -> "익명"
        String authorDisplay;
        if (isAnonymous) {
            authorDisplay = isMine ? "나(익명)" : "익명";
        } else {
            authorDisplay = post.getUser().getUsername();
        }

        return PostResponse.builder()
                .id(post.getId())
                .category(post.getBoardType().getBoardName())
                .title(post.getTitle())
                .content(post.getContent())
                .author(authorDisplay)
                .anonymous(isAnonymous)
                .isMine(isMine)
                .createdAt(post.getCreatedAt().toString())
                .views(post.getViewCount() == null ? 0 : post.getViewCount())
                .replies(post.getCommentCount() == null ? 0 : post.getCommentCount())
                .comments(comments)
                .build();
    }
}
