// src/main/java/kr/ac/dbapp/team1/gradchecker/dto/CommentResponse.java
package kr.ac.dbapp.team1.gradchecker.dto;

import com.fasterxml.jackson.annotation.JsonProperty; // 추가
import kr.ac.dbapp.team1.gradchecker.domain.Comment;
import lombok.Builder;
import lombok.Getter;

@Getter
@Builder
public class CommentResponse {

    private Long id;
    private Long parentId;
    private String author;

    // 응답 JSON 키는 "isAnonymous" 로 고정
    @JsonProperty("isAnonymous")
    private boolean anonymous;

    private boolean isMine;
    private String content;
    private String createdAt;

    public static CommentResponse from(Comment c, Long currentUserId) {
        boolean isMine = currentUserId != null
                && c.getUser().getUserId().equals(currentUserId);

        boolean isAnonymous = Boolean.TRUE.equals(c.getIsAnonymous());

        // 🔽 author 표시 문자열 가공
        String authorDisplay;
        if (isAnonymous) {
            authorDisplay = isMine ? "나(익명)" : "익명";
        } else {
            authorDisplay = c.getUser().getUsername();
        }

        return CommentResponse.builder()
                .id(c.getId())
                .parentId(c.getParentComment() != null ? c.getParentComment().getId() : null)
                .author(authorDisplay)
                .anonymous(isAnonymous)
                .isMine(isMine)
                .content(c.getContent())
                .createdAt(c.getCreatedAt().toString())
                .build();
    }
}
