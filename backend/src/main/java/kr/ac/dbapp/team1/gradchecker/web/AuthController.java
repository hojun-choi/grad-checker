// src/main/java/kr/ac/dbapp/team1/gradchecker/web/AuthController.java
package kr.ac.dbapp.team1.gradchecker.web;

import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpSession;
import jakarta.validation.Valid;
import kr.ac.dbapp.team1.gradchecker.domain.User;
import kr.ac.dbapp.team1.gradchecker.dto.AuthResponse;
import kr.ac.dbapp.team1.gradchecker.dto.LoginRequest;
import kr.ac.dbapp.team1.gradchecker.dto.RegisterRequest;
import kr.ac.dbapp.team1.gradchecker.service.AuthService;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.core.context.SecurityContext;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.web.context.HttpSessionSecurityContextRepository;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/auth")
public class AuthController {

    private final AuthService authService;

    public AuthController(AuthService authService) {
        this.authService = authService;
    }

    /**
     * [아이디 중복확인] GET /api/auth/check-login-id?loginId=...
     *
     * 프론트에서 기대하는 응답:
     * { "available": true } 또는 { "available": false }
     */
    @GetMapping("/check-login-id")
    public ResponseEntity<?> checkLoginId(@RequestParam("loginId") String loginId) {
        if (loginId == null || loginId.trim().isEmpty()) {
            return ResponseEntity.badRequest()
                    .body(Map.of("message", "loginId는 비어 있을 수 없습니다."));
        }

        boolean available = authService.isLoginIdAvailable(loginId.trim());
        return ResponseEntity.ok(Map.of("available", available));
    }

    /**
     * [회원가입] POST /api/auth/register
     */
    @PostMapping("/register")
    public ResponseEntity<?> register(@Valid @RequestBody RegisterRequest request) {
        try {
            User user = authService.register(request);
            return ResponseEntity.ok(Map.of(
                    "message", "회원가입 성공",
                    "username", user.getUsername()
            ));
        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest()
                    .body(Map.of("message", e.getMessage()));
        }
    }

    /**
     * [로그인] POST /api/auth/login
     *
     * 프론트에서 보내는 JSON 예시:
     * {
     *   "loginId": "hojun123",
     *   "password": "pw123456"
     * }
     */
    @PostMapping("/login")
    public ResponseEntity<?> login(
            @Valid @RequestBody LoginRequest request,
            HttpServletRequest httpRequest
    ) {
        try {
            // 1) 아이디/비번 직접 검사
            User user = authService.authenticate(request.loginId(), request.password());

            // 2) 인증 객체 만들어 SecurityContext + 세션에 저장
            Authentication authentication =
                    new UsernamePasswordAuthenticationToken(user, null, user.getAuthorities());

            SecurityContext context = SecurityContextHolder.createEmptyContext();
            context.setAuthentication(authentication);
            SecurityContextHolder.setContext(context);

            HttpSession session = httpRequest.getSession(true);
            session.setAttribute(
                    HttpSessionSecurityContextRepository.SPRING_SECURITY_CONTEXT_KEY,
                    context
            );

            // 3) 응답 DTO 생성
            AuthResponse response = authService.generateAuthResponse(authentication);
            return ResponseEntity.ok(response);

        } catch (IllegalArgumentException e) {
            // 아이디/비번 틀린 경우
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                    .body(Map.of("message", "아이디 또는 비밀번호가 올바르지 않습니다."));
        } catch (Exception e) {
            // 그 외 예외는 500
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Map.of("message", "로그인 처리 중 오류가 발생했습니다."));
        }
    }

    /**
     * [현재 사용자 조회] GET /api/auth/me
     */
    @GetMapping("/me")
    public ResponseEntity<?> me(@AuthenticationPrincipal User user) {
        if (user == null) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).build();
        }

        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        AuthResponse response = authService.generateAuthResponse(authentication);

        return ResponseEntity.ok(response);
    }

    /**
     * [로그아웃] POST /api/auth/logout
     */
    @PostMapping("/logout")
    public ResponseEntity<?> logout() {
        // 세션/컨텍스트 정리는 Spring Security 쪽 필터가 처리하므로 여기서는 204만 응답
        return ResponseEntity.noContent().build();
    }
}
