package kr.ac.dbapp.team1.gradchecker.dto;

import com.fasterxml.jackson.annotation.JsonAlias; // 추가
import jakarta.validation.constraints.NotBlank;
import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
public class CommentRequest {

    private Long parentCommentId;

    @NotBlank
    private String content;

    // [수정] 댓글 작성 시 프론트엔드가 'isAnonymous'로 보내므로 꼭 필요
    @JsonAlias("isAnonymous")
    private boolean anonymous;
}