// src/main/java/kr/ac/dbapp/team1/gradchecker/dto/CommentRequest.java
package kr.ac.dbapp.team1.gradchecker.dto;

import jakarta.validation.constraints.NotBlank;
import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
public class CommentRequest {

    private Long parentCommentId; // 대댓글이면 부모 ID, 아니면 null

    @NotBlank
    private String content;

    private boolean anonymous;
}
