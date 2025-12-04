// src/main/java/kr/ac/dbapp/team1/gradchecker/dto/CommentResponse.java
package kr.ac.dbapp.team1.gradchecker.dto;

import kr.ac.dbapp.team1.gradchecker.domain.Comment;
import lombok.Builder;
import lombok.Getter;

@Getter
@Builder
public class CommentResponse {

    private Long id;
    private Long parentId;
    private String author;
    private boolean anonymous;
    private String content;
    private String createdAt;

    public static CommentResponse from(Comment c) {
        return CommentResponse.builder()
                .id(c.getId())
                .parentId(c.getParentComment() != null ? c.getParentComment().getId() : null)
                .author(c.getUser().getUsername())
                .anonymous(Boolean.TRUE.equals(c.getIsAnonymous()))
                .content(c.getContent())
                .createdAt(c.getCreatedAt().toString())
                .build();
    }
}
