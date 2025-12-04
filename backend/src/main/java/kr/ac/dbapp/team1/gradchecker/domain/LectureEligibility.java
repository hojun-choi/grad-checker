// src/main/java/kr/ac/dbapp/team1/gradchecker/domain/LectureEligibility.java
package kr.ac.dbapp.team1.gradchecker.domain;

import jakarta.persistence.*;
import lombok.*;

@Entity
@Table(name = "lecture_eligibility")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class LectureEligibility {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    // FK -> lecture_timetable.id
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "lecture_id", nullable = false)
    private LectureTimetable lecture;

    // 전기/전선/전필/교필/교선/채플/융필/융선/연계1/연계2/연선/교직/교직전공 ...
    @Column(name = "category_type", nullable = false, length = 30)
    private String categoryType;

    // 학과/전공명 (tt_major랑 매칭)
    @Column(name = "department_name")
    private String departmentName;
}
