package kr.ac.dbapp.team1.gradchecker.domain;

import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDate;

@Entity
@Table(name = "rag_references")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class RagReference {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    // rag_logs.id FK
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "rag_log_id", nullable = false)
    private RagLog ragLog;

    // 1) 메타데이터
    @Column(name = "title", nullable = false, length = 255)
    private String title;

    @Column(name = "department", length = 100)
    private String department;

    @Column(name = "link", nullable = false, length = 1000)
    private String link;

    @Column(name = "published_date")
    private LocalDate publishedDate;

    // 2) 점수들 (nullable)
    @Column(name = "rrf_score")
    private Double rrfScore;

    @Column(name = "combined_score")
    private Double combinedScore;

    @Column(name = "recency_score")
    private Double recencyScore;
}
