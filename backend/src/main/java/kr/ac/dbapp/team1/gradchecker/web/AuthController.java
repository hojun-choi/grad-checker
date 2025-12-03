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
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.core.context.SecurityContext;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.web.context.HttpSessionSecurityContextRepository;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/auth")
public class AuthController {

    private final AuthService authService;
    private final AuthenticationManager authenticationManager;

    public AuthController(
            AuthService authService,
            AuthenticationManager authenticationManager
    ) {
        this.authService = authService;
        this.authenticationManager = authenticationManager;
    }

    /**
     * [아이디 중복확인] GET /auth/check-login-id?loginId=...
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
     * [회원가입] POST /auth/register
     *
     * 프론트에서 보내는 JSON 예시:
     * {
     *   "loginId": "hojun123",
     *   "password": "pw123456",
     *   "username": "최호준",
     *   "studentId": 20203137,
     *   "majorId": 1
     * }
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
     * [로그인] POST /auth/login
     *
     * 프론트에서 보내는 JSON 예시:
     * {
     *   "loginId": "hojun123",
     *   "password": "pw123456"
     * }
     *
     * LoginRequest 는 loginId / password 필드를 가져야 한다.
     */
    @PostMapping("/login")
    public ResponseEntity<?> login(
            @Valid @RequestBody LoginRequest request,
            HttpServletRequest httpRequest
    ) {
        try {
            Authentication authentication = authenticationManager.authenticate(
                    new UsernamePasswordAuthenticationToken(
                            // 🔥 username 대신 loginId 로 인증
                            request.loginId(),
                            request.password()
                    )
            );

            SecurityContext context = SecurityContextHolder.createEmptyContext();
            context.setAuthentication(authentication);
            SecurityContextHolder.setContext(context);

            HttpSession session = httpRequest.getSession(true);
            session.setAttribute(
                    HttpSessionSecurityContextRepository.SPRING_SECURITY_CONTEXT_KEY,
                    context
            );

            AuthResponse response = authService.generateAuthResponse(authentication);
            return ResponseEntity.ok(response);

        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                    .body(Map.of("message", "아이디 또는 비밀번호가 올바르지 않습니다."));
        }
    }

    /**
     * [현재 사용자 조회] GET /auth/me
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
     * [로그아웃] POST /auth/logout
     */
    @PostMapping("/logout")
    public ResponseEntity<?> logout() {
        return ResponseEntity.noContent().build();
    }
}
