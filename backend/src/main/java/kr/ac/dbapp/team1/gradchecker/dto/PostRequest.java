package kr.ac.dbapp.team1.gradchecker.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
public class PostRequest {

    // userId는 Controller에서 인증 정보를 통해 주입되므로 DTO에서 제거합니다.
    @NotNull(message = "게시판 종류 ID는 필수입니다.")
    private Long boardTypeId;

    @NotBlank(message = "제목은 필수 입력 사항입니다.")
    @Size(max = 200, message = "제목은 200자 이하로 입력해주세요.")
    private String title;

    @NotBlank(message = "내용은 필수 입력 사항입니다.")
    private String content;
}