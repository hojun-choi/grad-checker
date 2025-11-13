package kr.ac.dbapp.team1.gradchecker.dto;

import lombok.Getter;
import lombok.Setter;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;


@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class RegisterRequest {

    // 사용자가 입력한 ID/이름을 받는 필드
    private String username;

    // 비밀번호 필드
    private String password;

    // (선택) 이메일 필드
    private String email;
}