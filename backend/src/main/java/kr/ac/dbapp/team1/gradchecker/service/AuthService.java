// src/main/java/kr/ac/dbapp/team1/gradchecker/service/AuthService.java
package kr.ac.dbapp.team1.gradchecker.service;

import kr.ac.dbapp.team1.gradchecker.domain.User;
import kr.ac.dbapp.team1.gradchecker.dto.AuthResponse;
import kr.ac.dbapp.team1.gradchecker.dto.RegisterRequest;
import kr.ac.dbapp.team1.gradchecker.repo.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class AuthService {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;

    /**
     * [아이디 중복확인] loginId 사용 가능 여부
     *  - 컨트롤러: GET /api/auth/check-login-id?loginId=...
     */
    @Transactional(readOnly = true)
    public boolean isLoginIdAvailable(String loginId) {
        if (loginId == null || loginId.trim().isEmpty()) {
            return false;
        }
        return !userRepository.existsByLoginId(loginId.trim());
    }

    /**
     * [회원가입] 사용자 정보를 저장소에 저장하고, 비밀번호를 해싱합니다.
     *
     * users 테이블 구조:
     *  - login_id    (로그인용 ID)
     *  - password_hash
     *  - username    (실제 이름)
     *  - student_id  (학번)
     *  - major_id    (FK -> major.id)
     */
    @Transactional
    public User register(RegisterRequest request) {

        String loginId   = request.getLoginId();
        String username  = request.getUsername();
        Long   studentId = request.getStudentId();
        Long   majorId   = request.getMajorId();

        // 0. 기본 값 검증
        if (loginId == null || loginId.trim().isEmpty()) {
            throw new IllegalArgumentException("로그인 ID는 필수입니다.");
        }
        if (username == null || username.trim().isEmpty()) {
            throw new IllegalArgumentException("이름은 필수입니다.");
        }
        if (studentId == null) {
            throw new IllegalArgumentException("학번은 필수입니다.");
        }
        if (majorId == null) {
            throw new IllegalArgumentException("전공(majorId)은 필수입니다.");
        }

        // 1. loginId 중복 체크
        if (userRepository.existsByLoginId(loginId.trim())) {
            throw new IllegalArgumentException("이미 사용 중인 로그인 ID입니다.");
        }

        // 2. 비밀번호 해싱 (Bcrypt 등)
        String hashedPassword = passwordEncoder.encode(request.getPassword());

        // 3. User 엔티티 생성 및 DB 저장
        User newUser = User.builder()
                .loginId(loginId.trim())
                .username(username.trim())
                .passwordHash(hashedPassword)
                .studentId(studentId)
                .majorId(majorId)
                .isDeleted(false)
                .build();

        return userRepository.save(newUser);
    }

    /**
     * [로그인] 아이디/비밀번호 직접 검증
     *  - loginId로 유저를 찾고, passwordEncoder.matches(raw, hashed)로 검사.
     *  - 실패 시 IllegalArgumentException 발생.
     */
    @Transactional(readOnly = true)
    public User authenticate(String loginId, String rawPassword) {
        if (loginId == null || rawPassword == null) {
            throw new IllegalArgumentException("아이디 또는 비밀번호가 올바르지 않습니다.");
        }

        User user = userRepository.findByLoginId(loginId.trim())
                .orElseThrow(() -> new IllegalArgumentException("아이디 또는 비밀번호가 올바르지 않습니다."));

        // 🔐 Bcrypt 등 해시 비교
        if (!passwordEncoder.matches(rawPassword, user.getPasswordHash())) {
            throw new IllegalArgumentException("아이디 또는 비밀번호가 올바르지 않습니다.");
        }

        if (Boolean.TRUE.equals(user.getIsDeleted())) {
            throw new IllegalArgumentException("비활성화된 계정입니다.");
        }

        return user;
    }

    /**
     * Authentication 객체에서 사용자 정보를 추출하여 응답 DTO를 생성합니다.
     *
     * /auth/login, /auth/me 에서 공통으로 사용됨.
     */
    public AuthResponse generateAuthResponse(Authentication authentication) {
        User userDetails = (User) authentication.getPrincipal();

        List<String> roles = userDetails.getAuthorities().stream()
                .map(GrantedAuthority::getAuthority)
                .map(role -> role.replace("ROLE_", ""))
                .collect(Collectors.toList());

        // 지금 구조에서는 catalogYear 같은 건 없으니 일단 null 유지
        return AuthResponse.builder()
                .username(userDetails.getUsername())
                .roles(roles)
                .catalogYear(null)
                .build();
    }
}
