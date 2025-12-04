// src/main/java/kr/ac/dbapp/team1/gradchecker/dto/PostRequest.java
package kr.ac.dbapp.team1.gradchecker.dto;

import jakarta.validation.constraints.NotBlank;
import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
public class PostRequest {

    /**
     * 어떤 게시판에 쓸 건지 (예: "졸업", "시간표" 등)
     * - board_types.board_name 과 매칭
     */
    @NotBlank
    private String boardName;

    @NotBlank
    private String title;

    @NotBlank
    private String content;

    private boolean anonymous;
}
