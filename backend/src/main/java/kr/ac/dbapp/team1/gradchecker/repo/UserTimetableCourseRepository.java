// src/main/java/kr/ac/dbapp/team1/gradchecker/repo/UserTimetableCourseRepository.java
package kr.ac.dbapp.team1.gradchecker.repo;

import kr.ac.dbapp.team1.gradchecker.domain.UserTimetableCourse;
import kr.ac.dbapp.team1.gradchecker.dto.TimetableClassProjection;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;

public interface UserTimetableCourseRepository extends JpaRepository<UserTimetableCourse, Long> {

    // 1) 특정 user_timetable 에 들어있는 모든 과목 + lecture_schedule 조인
    @Query(value = """
        SELECT
          lt.id AS lectureId,
          CASE ls.meeting_day
            WHEN '월' THEN 0
            WHEN '화' THEN 1
            WHEN '수' THEN 2
            WHEN '목' THEN 3
            WHEN '금' THEN 4
            ELSE 0
          END AS day,
          TIME_TO_SEC(ls.start_time) / 3600 AS start,
          TIME_TO_SEC(ls.end_time) / 3600 AS end,
          lt.course_title AS name,
          ls.building_room AS room
        FROM user_timetable_course utc
        JOIN lecture_timetable lt
          ON utc.lecture_timetable_id = lt.id
        JOIN lecture_schedule ls
          ON ls.lecture_id = lt.id
        WHERE utc.user_timetable_id = :timetableId
        """, nativeQuery = true)
    List<TimetableClassProjection> findClassesByTimetableId(@Param("timetableId") Long timetableId);

    // 2) 방금 추가한 한 과목만 다시 가져오고 싶을 때
    @Query(value = """
        SELECT
          lt.id AS lectureId,
          CASE ls.meeting_day
            WHEN '월' THEN 0
            WHEN '화' THEN 1
            WHEN '수' THEN 2
            WHEN '목' THEN 3
            WHEN '금' THEN 4
            ELSE 0
          END AS day,
          TIME_TO_SEC(ls.start_time) / 3600 AS start,
          TIME_TO_SEC(ls.end_time) / 3600 AS end,
          lt.course_title AS name,
          ls.building_room AS room
        FROM user_timetable_course utc
        JOIN lecture_timetable lt
          ON utc.lecture_timetable_id = lt.id
        JOIN lecture_schedule ls
          ON ls.lecture_id = lt.id
        WHERE utc.user_timetable_id = :timetableId
          AND utc.lecture_timetable_id = :lectureTimetableId
        """, nativeQuery = true)
    List<TimetableClassProjection> findClassByTimetableAndLecture(
            @Param("timetableId") Long timetableId,
            @Param("lectureTimetableId") Long lectureTimetableId
    );
}