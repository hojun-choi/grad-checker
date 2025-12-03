package kr.ac.dbapp.team1.gradchecker.domain;

import jakarta.persistence.*;
import lombok.*;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.userdetails.UserDetails;

import java.time.LocalDateTime;
import java.util.Collection;
import java.util.List;

@Entity
@Table(name = "users")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class User implements UserDetails {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id") // DB 컬럼명과 맞추기
    private Long userId;

    @Column(name = "login_id", nullable = false, unique = true, length = 50)
    private String loginId;

    @Column(name = "password_hash", nullable = false)
    private String passwordHash;

    /**
     * 실제 이름 (users.username)
     */
    @Column(name = "username", nullable = false, length = 50)
    private String username;

    /**
     * (선택) 이메일 – DB에 email 컬럼이 있을 때만 사용
     */
    @Column(name = "email", length = 120, nullable = true)
    private String email;

    /**
     * 학번 (users.student_id)
     */
    @Column(name = "student_id", nullable = false)
    private Long studentId;

    /**
     * 전공 PK (users.major_id, FK -> major.id)
     */
    @Column(name = "major_id", nullable = false)
    private Long majorId;

    // 생성/수정일, 삭제 플래그
    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @Column(name = "updated_at", nullable = false)
    private LocalDateTime updatedAt;

    @Column(name = "is_deleted", nullable = false)
    private Boolean isDeleted = false;

    @PrePersist
    protected void onCreate() {
        LocalDateTime now = LocalDateTime.now();
        this.createdAt = now;
        this.updatedAt = now;
    }

    @PreUpdate
    protected void onUpdate() {
        this.updatedAt = LocalDateTime.now();
    }

    // ==============================
    // UserDetails 구현부
    // ==============================
    @Override
    public Collection<? extends GrantedAuthority> getAuthorities() {
        // 기본 ROLE_STUDENT 부여
        return List.of(new SimpleGrantedAuthority("ROLE_STUDENT"));
    }

    @Override
    public String getPassword() {
        return passwordHash;
    }

    /**
     * Spring Security 상의 username은 loginId로 사용
     */
    @Override
    public String getUsername() {
        return loginId;
    }

    @Override
    public boolean isAccountNonExpired() {
        return true;
    }

    @Override
    public boolean isAccountNonLocked() {
        return !Boolean.TRUE.equals(isDeleted);
    }

    @Override
    public boolean isCredentialsNonExpired() {
        return true;
    }

    @Override
    public boolean isEnabled() {
        return !Boolean.TRUE.equals(isDeleted);
    }
}
