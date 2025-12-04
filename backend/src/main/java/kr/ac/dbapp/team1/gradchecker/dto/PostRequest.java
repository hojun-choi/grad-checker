package kr.ac.dbapp.team1.gradchecker.dto;

import com.fasterxml.jackson.annotation.JsonAlias; // 추가
import jakarta.validation.constraints.NotBlank;
import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
public class PostRequest {

    @NotBlank
    private String boardName;

    @NotBlank
    private String title;

    @NotBlank
    private String content;

    // [수정] 프론트엔드가 'anonymous' 또는 'isAnonymous' 둘 중 뭘 보내도 처리 가능하게 함
    @JsonAlias("isAnonymous") 
    private boolean anonymous;
}