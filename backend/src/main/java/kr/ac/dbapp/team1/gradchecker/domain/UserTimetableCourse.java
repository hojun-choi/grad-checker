// src/main/java/kr/ac/dbapp/team1/gradchecker/domain/UserTimetableCourse.java
package kr.ac.dbapp.team1.gradchecker.domain;

import jakarta.persistence.*;
import lombok.*;

@Entity
@Table(name = "user_timetable_course")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class UserTimetableCourse {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    // FK -> user_timetable.id
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_timetable_id", nullable = false)
    private UserTimetable userTimetable;

    // FK -> lecture_timetable.id
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "lecture_timetable_id", nullable = false)
    private LectureTimetable lectureTimetable;
}
