// src/main/java/kr/ac/dbapp/team1/gradchecker/domain/UserTimetable.java
package kr.ac.dbapp.team1.gradchecker.domain;

import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

@Entity
@Table(name = "user_timetable")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class UserTimetable {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    // FK -> user.id
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", nullable = false)
    private User user;

    @Column(nullable = false)
    private Integer year;

    @Column(nullable = false, length = 20)
    private String semester;

    @Column(name = "timetable_name", nullable = false)
    private String name;

    @Column(name = "is_main", nullable = false)
    private boolean isMain;

    @OneToMany(mappedBy = "userTimetable", cascade = CascadeType.ALL, orphanRemoval = true)
    @Builder.Default
    private List<UserTimetableCourse> courses = new ArrayList<>();

    @Column(name = "created_at", nullable = false)
    private LocalDateTime createdAt;

    @Column(name = "updated_at", nullable = false)
    private LocalDateTime updatedAt;

    @PrePersist
    public void onCreate() {
        this.createdAt = LocalDateTime.now();
        this.updatedAt = this.createdAt;
    }

    @PreUpdate
    public void onUpdate() {
        this.updatedAt = LocalDateTime.now();
    }

    public void addCourse(UserTimetableCourse course) {
        courses.add(course);
        course.setUserTimetable(this);
    }

    public void removeCourse(UserTimetableCourse course) {
        courses.remove(course);
        course.setUserTimetable(null);
    }
}
