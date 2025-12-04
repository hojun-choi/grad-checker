// src/main/java/kr/ac/dbapp/team1/gradchecker/domain/LectureTimetable.java
package kr.ac.dbapp.team1.gradchecker.domain;

import jakarta.persistence.*;
import lombok.*;

import java.math.BigDecimal;

// src/main/java/.../LectureTimetable.java
@Entity
@Table(name = "lecture_timetable")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class LectureTimetable {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private Integer year;

    @Column(nullable = false, length = 20)
    private String semester;

    @Column(name = "course_code", nullable = false, length = 30)
    private String courseCode;

    @Column(name = "course_title", nullable = false, length = 200)
    private String courseTitle;

    @Column(name = "section_no", length = 10)
    private String sectionNo;

    @Column(name = "instructor_name", length = 100)
    private String instructorName;

    @Column(name = "department_name", length = 100)
    private String departmentName;

    @Column(name = "domain", length = 200)
    private String domain;

    @Column(name = "course_credits", nullable = false)
    private Double courseCredits;

    @Column(name = "lecture_hours", nullable = false)
    private Double lectureHours;

    @Column(name = "design_credits", nullable = false)
    private Double designCredits;

    @Column(name = "capacity", nullable = false)
    private Integer capacity;

    @Column(name = "enrolled_count", nullable = false)
    private Integer enrolledCount;

    @Column(name = "class_type_info", length = 50)
    private String classTypeInfo;

    @Column(name = "taking_note")
    private String takingNote;

    @Column(name = "target_students", length = 200)
    private String targetStudents;

    @Column(name = "engineering_certification", length = 100)
    private String engineeringCertification;
}

