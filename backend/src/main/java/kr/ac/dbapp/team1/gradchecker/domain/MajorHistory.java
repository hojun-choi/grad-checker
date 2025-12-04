package kr.ac.dbapp.team1.gradchecker.domain;

import jakarta.persistence.*;
import lombok.*;
import java.time.LocalDateTime;

/**
 * major_history 테이블 매핑 엔티티
 *
 * CREATE TABLE major_history (
 *   id BIGINT AUTO_INCREMENT PRIMARY KEY,
 *   current_major_id BIGINT NOT NULL,
 *   year INT NOT NULL,
 *   college VARCHAR(100) NOT NULL,
 *   faculty VARCHAR(100) NOT NULL,
 *   tt_major VARCHAR(100) NOT NULL,
 *   major_name VARCHAR(100) NOT NULL,
 *   category VARCHAR(50) NOT NULL,
 *   is_deleted TINYINT(1) NOT NULL DEFAULT 0,
 *   created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
 *   updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
 * );
 */
@Entity
@Table(name = "major_history")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class MajorHistory {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    /**
     * major 테이블의 id (FK)
     * users.major_id 로도 이 값을 저장해서 사용함
     */
    @Column(name = "current_major_id", nullable = false)
    private Long currentMajorId;

    @Column(name = "year", nullable = false)
    private Integer year;

    @Column(name = "college", nullable = false, length = 100)
    private String college;

    @Column(name = "faculty", nullable = false, length = 100)
    private String faculty;

    @Column(name = "tt_major", nullable = false, length = 100)
    private String ttMajor;

    @Column(name = "major_name", nullable = false, length = 100)
    private String majorName;

    @Column(name = "category", nullable = false, length = 50)
    private String category;

    @Builder.Default
    @Column(name = "is_deleted", nullable = false)
    private Boolean isDeleted = false;

    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @Column(name = "updated_at", nullable = false)
    private LocalDateTime updatedAt;

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
}
