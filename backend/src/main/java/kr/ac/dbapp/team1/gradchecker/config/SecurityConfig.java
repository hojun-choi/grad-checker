package kr.ac.dbapp.team1.gradchecker.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.dao.DaoAuthenticationProvider;
import org.springframework.security.config.annotation.authentication.configuration.AuthenticationConfiguration;
import org.springframework.security.config.annotation.method.configuration.EnableMethodSecurity;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.csrf.CookieCsrfTokenRepository;
import org.springframework.security.web.csrf.CsrfTokenRequestAttributeHandler;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.CorsConfigurationSource;
import org.springframework.web.cors.UrlBasedCorsConfigurationSource;

import java.util.List;

@Configuration
@EnableWebSecurity
@EnableMethodSecurity
public class SecurityConfig {

    private final UserDetailsService userDetailsService;

    public SecurityConfig(UserDetailsService userDetailsService) {
        this.userDetailsService = userDetailsService;
    }

    // ==========================
    // Password / Auth Provider
    // ==========================
    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }

    @Bean
    public DaoAuthenticationProvider authenticationProvider() {
        DaoAuthenticationProvider authProvider = new DaoAuthenticationProvider();
        authProvider.setUserDetailsService(userDetailsService);
        authProvider.setPasswordEncoder(passwordEncoder());
        return authProvider;
    }

    @Bean
    public AuthenticationManager authenticationManager(
            AuthenticationConfiguration authConfig
    ) throws Exception {
        return authConfig.getAuthenticationManager();
    }

    // ==========================
    // Security Filter Chain
    // ==========================
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {

        CookieCsrfTokenRepository tokenRepository = CookieCsrfTokenRepository.withHttpOnlyFalse();
        CsrfTokenRequestAttributeHandler requestHandler = new CsrfTokenRequestAttributeHandler();

        http
                // CORS 설정
                .cors(cors -> cors.configurationSource(corsConfigurationSource()))

                // CSRF 설정 (쿠키 기반)
                .csrf(csrf -> csrf
                        .csrfTokenRepository(tokenRepository)
                        .csrfTokenRequestHandler(requestHandler)
                        // 정적 리소스, index.html 등은 CSRF 대상에서 제외
                        .ignoringRequestMatchers(
                                "/", "/index.html",
                                "/assets/**",
                                "/favicon.ico",
                                "/error"
                        )
                )

                .httpBasic(basic -> basic.disable())
                .formLogin(form -> form.disable())

                // 권한 설정
                .authorizeHttpRequests(auth -> auth
                        // 프론트 엔트리 + 정적 파일 + 공용 API 들은 전부 허용
                        .requestMatchers(
                                "/", "/index.html",
                                "/assets/**",
                                "/favicon.ico",
                                "/error",
                                "/api/auth/**"
                        ).permitAll()
                        // 나머지도 지금은 전부 허용 (추후 인증 붙이면 여기 수정)
                        .anyRequest().permitAll()
                )

                // 세션 관리 및 로그아웃
                .sessionManagement(session -> session
                        .sessionCreationPolicy(SessionCreationPolicy.ALWAYS)
                        .maximumSessions(1)
                        .maxSessionsPreventsLogin(false)
                )
                .logout(logout -> logout
                        .logoutUrl("/api/auth/logout")
                        .invalidateHttpSession(true)
                        .deleteCookies("JSESSIONID", "XSRF-TOKEN")
                )

                .authenticationProvider(authenticationProvider());

        return http.build();
    }

    // ==========================
    // CORS 설정
    // ==========================
    @Bean
    public CorsConfigurationSource corsConfigurationSource() {
        CorsConfiguration config = new CorsConfiguration();

        // 로컬 Vite + ngrok 도메인들 허용
        config.setAllowedOriginPatterns(List.of(
                "http://localhost:5173",
                "http://127.0.0.1:5173",
                "https://*.ngrok-free.app",
                "https://*.ngrok-free.dev"
        ));

        config.setAllowedMethods(List.of("GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"));
        config.setAllowedHeaders(List.of("*"));
        config.setAllowCredentials(true);

        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", config);
        return source;
    }
}
