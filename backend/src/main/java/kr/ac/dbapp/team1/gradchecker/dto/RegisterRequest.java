package kr.ac.dbapp.team1.gradchecker.dto;

import lombok.Getter;
import lombok.Setter;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;

/**
 * 회원가입 요청 DTO
 *
 * users 테이블 기준:
 *  - login_id   : loginId
 *  - password_hash : password (서버에서 해싱)
 *  - username   : username (실제 이름)
 *  - student_id : studentId
 *  - major_id   : majorId
 *
 * (email은 선택값으로 두고 싶으면 유지)
 */
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class RegisterRequest {

    /** 로그인에 사용할 ID (users.login_id) */
    private String loginId;

    /** 실제 이름 (users.username) */
    private String username;

    /** 비밀번호 (서버에서 해싱해서 password_hash에 저장) */
    private String password;

    /** 학번 (users.student_id, BIGINT) */
    private Long studentId;

    /** 전공 PK (users.major_id, BIGINT, FK -> major.id) */
    private Long majorId;
}
