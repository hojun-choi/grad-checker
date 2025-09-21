package kr.ac.dbapp.team1.gradchecker.domain;

import jakarta.persistence.*;
import lombok.*;

@Entity
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
@Table(name = "requirement_rule")
public class RequirementRule {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    /**
     * TOTAL / MAJOR / GE / ...
     */
    @Column(name = "group_code", nullable = false, length = 32)
    private String groupCode;

    /**
     * CREDITS_AT_LEAST / GE_AREA_AT_LEAST / INCLUDE_COURSES / ...
     */
    @Column(name = "rule_type", nullable = false, length = 64)
    private String ruleType;

    /**
     * 예: 2024
     */
    @Column(name = "catalog_year", nullable = false)
    private Integer catalogYear;

    /**
     * 규칙 파라미터 JSON
     * DB에는 TEXT로 생성되어 있으므로, 엔티티도 TEXT로 정확히 맞춘다.
     * (중요) tinytext가 아니라 text로!
     */
    @Column(name = "params_json", columnDefinition = "text")
    private String paramsJson;
}
