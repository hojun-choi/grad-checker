// src/main/java/kr/ac/dbapp/team1/gradchecker/dto/LoginRequest.java
package kr.ac.dbapp.team1.gradchecker.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import jakarta.validation.constraints.NotBlank;

public record LoginRequest(

        // 프론트에서 오는 JSON 키가 "username" 이므로 이렇게 매핑
        @NotBlank
        @JsonProperty("username")
        String loginId,

        @NotBlank
        String password
) {
}
