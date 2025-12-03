package kr.ac.dbapp.team1.gradchecker.domain;

import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

@Entity
@Table(name = "rag_logs")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class RagLog {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    // FK(users.id). 지금은 null 넣어도 되고, 나중에 로그인 붙이면 User에서 가져오면 됨.
    @Column(name = "user_id")
    private Long userId;

    @Column(name = "question", nullable = false, columnDefinition = "TEXT")
    private String question;

    @Column(name = "answer", nullable = false, columnDefinition = "MEDIUMTEXT")
    private String answer;

    // DB에서 CURRENT_TIMESTAMP 로 채우도록 insertable/updatable false
    @Column(name = "created_at", insertable = false, updatable = false)
    private LocalDateTime createdAt;

    @OneToMany(mappedBy = "ragLog", cascade = CascadeType.ALL, orphanRemoval = true)
    @Builder.Default
    private List<RagReference> references = new ArrayList<>();
}
