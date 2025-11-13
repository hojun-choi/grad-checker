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
     * [회원가입] 사용자 정보를 저장소에 저장하고, 비밀번호를 해싱합니다.
     */
    @Transactional
    public User register(RegisterRequest request) {

        // 1. 중복 체크
        if (userRepository.existsByLoginId(request.getUsername())) {
            throw new IllegalArgumentException("이미 사용 중인 로그인 ID입니다");
        }

        // 2. 비밀번호 해싱
        String hashedPassword = passwordEncoder.encode(request.getPassword());

        // 3. User 엔티티 생성 및 DB 저장 (Student 관계 및 학번 검증 로직 제거)
        User newUser = User.builder()
                .loginId(request.getUsername())
                .username(request.getUsername())
                .passwordHash(hashedPassword)
                .isDeleted(false)
                .build();

        return userRepository.save(newUser);
    }

    /**
     * Authentication 객체에서 사용자 정보를 추출하여 응답 DTO를 생성합니다.
     */
    public AuthResponse generateAuthResponse(Authentication authentication) {
        User userDetails = (User) authentication.getPrincipal();

        List<String> roles = userDetails.getAuthorities().stream()
                .map(GrantedAuthority::getAuthority)
                .map(role -> role.replace("ROLE_", ""))
                .collect(Collectors.toList());

        // Student 필드가 제거되었으므로, 관련 필드는 null 처리합니다.
        return AuthResponse.builder()
                .username(userDetails.getUsername())
                .roles(roles)
                .catalogYear(null) // Student 엔티티 제거로 인해 null
                .build();
    }
}