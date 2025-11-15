package kr.ac.dbapp.team1.gradchecker.dto;

import lombok.Getter;
import lombok.Setter;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

//댓글 작성 및 수정 API 요청 데이터 처리 DTO
@Getter
@Setter
public class CommentRequest {

    @NotBlank(message = "댓글 내용은 필수 입력 사항입니다.")
    @Size(max = 500, message = "댓글은 500자를 초과할 수 없습니다.")
    private String content;

    // 대댓글 작성을 위해 필요합니다. (NULL 허용)
    private Long parentCommentId;
}
