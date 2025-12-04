// src/main/java/kr/ac/dbapp/team1/gradchecker/repo/LectureTimetableRepository.java
package kr.ac.dbapp.team1.gradchecker.repo;

import kr.ac.dbapp.team1.gradchecker.domain.LectureTimetable;
import kr.ac.dbapp.team1.gradchecker.repo.projection.LectureSearchProjection;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;

public interface LectureTimetableRepository extends JpaRepository<LectureTimetable, Long> {

    // =========================
    //  전공(학부 전공) 강의 조회
    // =========================
    @Query(value = """
        SELECT
            lt.id              AS id,
            lt.year            AS year,
            lt.semester        AS semester,
            lt.course_code     AS courseCode,
            lt.course_title    AS courseTitle,
            lt.section_no      AS sectionNo,
            lt.instructor_name AS instructorName,
            lt.course_credits  AS courseCredits,
            lt.lecture_hours   AS lectureHours,
            lt.capacity        AS capacity,
            lt.enrolled_count  AS enrolledCount,
            -- ===== 시간/강의실은 lecture_schedule 에서 =====
            ls.meeting_day     AS meetingDay,
            ls.start_time      AS startTime,
            ls.end_time        AS endTime,
            ls.building_room   AS buildingRoom
        FROM lecture_timetable lt
        LEFT JOIN lecture_schedule ls
               ON ls.lecture_id = lt.id
        LEFT JOIN lecture_eligibility le
               ON le.lecture_id = lt.id
        WHERE lt.year = :year
          AND lt.semester = :semester
          AND le.department_name = :ttMajor          -- 전공(tt_major) 기준
          AND le.category_type IN ('전기','전선','전필')
        """, nativeQuery = true)
    List<LectureSearchProjection> findMajorLectures(
            @Param("year") int year,
            @Param("semester") String semester,
            @Param("ttMajor") String ttMajor
    );

    // =========================
    //  교양필수
    // =========================
    @Query(value = """
        SELECT
            lt.id              AS id,
            lt.year            AS year,
            lt.semester        AS semester,
            lt.course_code     AS courseCode,
            lt.course_title    AS courseTitle,
            lt.section_no      AS sectionNo,
            lt.instructor_name AS instructorName,
            lt.course_credits  AS courseCredits,
            lt.lecture_hours   AS lectureHours,
            lt.capacity        AS capacity,
            lt.enrolled_count  AS enrolledCount,
            ls.meeting_day     AS meetingDay,
            ls.start_time      AS startTime,
            ls.end_time        AS endTime,
            ls.building_room   AS buildingRoom
        FROM lecture_timetable lt
        LEFT JOIN lecture_schedule ls
               ON ls.lecture_id = lt.id
        WHERE lt.year = :year
          AND lt.semester = :semester
          AND lt.domain LIKE '교필%%'
        """, nativeQuery = true)
    List<LectureSearchProjection> findCoreLectures(
            @Param("year") int year,
            @Param("semester") String semester
    );

    // =========================
    //  교양선택 (domain 부분 일치 검색)
    // =========================
    @Query(value = """
        SELECT
            lt.id              AS id,
            lt.year            AS year,
            lt.semester        AS semester,
            lt.course_code     AS courseCode,
            lt.course_title    AS courseTitle,
            lt.section_no      AS sectionNo,
            lt.instructor_name AS instructorName,
            lt.course_credits  AS courseCredits,
            lt.lecture_hours   AS lectureHours,
            lt.capacity        AS capacity,
            lt.enrolled_count  AS enrolledCount,
            ls.meeting_day     AS meetingDay,
            ls.start_time      AS startTime,
            ls.end_time        AS endTime,
            ls.building_room   AS buildingRoom
        FROM lecture_timetable lt
        LEFT JOIN lecture_schedule ls
               ON ls.lecture_id = lt.id
        WHERE lt.year = :year
          AND lt.semester = :semester
          AND (:domain IS NULL OR lt.domain LIKE CONCAT('%%', :domain, '%%'))
        """, nativeQuery = true)
    List<LectureSearchProjection> findElectiveLectures(
            @Param("year") int year,
            @Param("semester") String semester,
            @Param("domain") String domain
    );

    // =========================
    //  채플  (lecture_eligibility.category_type = '채플')
    // =========================
    @Query(value = """
        SELECT
            lt.id              AS id,
            lt.year            AS year,
            lt.semester        AS semester,
            lt.course_code     AS courseCode,
            lt.course_title    AS courseTitle,
            lt.section_no      AS sectionNo,
            lt.instructor_name AS instructorName,
            lt.course_credits  AS courseCredits,
            lt.lecture_hours   AS lectureHours,
            lt.capacity        AS capacity,
            lt.enrolled_count  AS enrolledCount,
            ls.meeting_day     AS meetingDay,
            ls.start_time      AS startTime,
            ls.end_time        AS endTime,
            ls.building_room   AS buildingRoom
        FROM lecture_timetable lt
        LEFT JOIN lecture_schedule ls
               ON ls.lecture_id = lt.id
        LEFT JOIN lecture_eligibility le
               ON le.lecture_id = lt.id
        WHERE lt.year = :year
          AND lt.semester = :semester
          AND le.category_type = '채플'
        """, nativeQuery = true)
    List<LectureSearchProjection> findChapelLectures(
            @Param("year") int year,
            @Param("semester") String semester
    );

    // =========================
    //  교직 (lecture_eligibility.category_type LIKE '교직%')
    // =========================
    @Query(value = """
        SELECT
            lt.id              AS id,
            lt.year            AS year,
            lt.semester        AS semester,
            lt.course_code     AS courseCode,
            lt.course_title    AS courseTitle,
            lt.section_no      AS sectionNo,
            lt.instructor_name AS instructorName,
            lt.course_credits  AS courseCredits,
            lt.lecture_hours   AS lectureHours,
            lt.capacity        AS capacity,
            lt.enrolled_count  AS enrolledCount,
            ls.meeting_day     AS meetingDay,
            ls.start_time      AS startTime,
            ls.end_time        AS endTime,
            ls.building_room   AS buildingRoom
        FROM lecture_timetable lt
        LEFT JOIN lecture_schedule ls
               ON ls.lecture_id = lt.id
        LEFT JOIN lecture_eligibility le
               ON le.lecture_id = lt.id
        WHERE lt.year = :year
          AND lt.semester = :semester
          AND le.category_type LIKE '교직%%'
        """, nativeQuery = true)
    List<LectureSearchProjection> findTeachingLectures(
            @Param("year") int year,
            @Param("semester") String semester
    );

    // =========================
    //  연계전공 (category_type LIKE '연계%' + department_name = ttMajor)
    // =========================
    @Query(value = """
        SELECT
            lt.id              AS id,
            lt.year            AS year,
            lt.semester        AS semester,
            lt.course_code     AS courseCode,
            lt.course_title    AS courseTitle,
            lt.section_no      AS sectionNo,
            lt.instructor_name AS instructorName,
            lt.course_credits  AS courseCredits,
            lt.lecture_hours   AS lectureHours,
            lt.capacity        AS capacity,
            lt.enrolled_count  AS enrolledCount,
            ls.meeting_day     AS meetingDay,
            ls.start_time      AS startTime,
            ls.end_time        AS endTime,
            ls.building_room   AS buildingRoom
        FROM lecture_timetable lt
        LEFT JOIN lecture_schedule ls
               ON ls.lecture_id = lt.id
        LEFT JOIN lecture_eligibility le
               ON le.lecture_id = lt.id
        WHERE lt.year = :year
          AND lt.semester = :semester
          AND le.department_name = :ttMajor
          AND le.category_type LIKE '연계%%'
        """, nativeQuery = true)
    List<LectureSearchProjection> findLinkedMajorLectures(
            @Param("year") int year,
            @Param("semester") String semester,
            @Param("ttMajor") String ttMajor
    );

    // =========================
    //  융합전공 (category_type IN ('융필','융선') + department_name = ttMajor)
    // =========================
    @Query(value = """
        SELECT
            lt.id              AS id,
            lt.year            AS year,
            lt.semester        AS semester,
            lt.course_code     AS courseCode,
            lt.course_title    AS courseTitle,
            lt.section_no      AS sectionNo,
            lt.instructor_name AS instructorName,
            lt.course_credits  AS courseCredits,
            lt.lecture_hours   AS lectureHours,
            lt.capacity        AS capacity,
            lt.enrolled_count  AS enrolledCount,
            ls.meeting_day     AS meetingDay,
            ls.start_time      AS startTime,
            ls.end_time        AS endTime,
            ls.building_room   AS buildingRoom
        FROM lecture_timetable lt
        LEFT JOIN lecture_schedule ls
               ON ls.lecture_id = lt.id
        LEFT JOIN lecture_eligibility le
               ON le.lecture_id = lt.id
        WHERE lt.year = :year
          AND lt.semester = :semester
          AND le.department_name = :ttMajor
          AND le.category_type IN ('융필','융선')
        """, nativeQuery = true)
    List<LectureSearchProjection> findConvergenceMajorLectures(
            @Param("year") int year,
            @Param("semester") String semester,
            @Param("ttMajor") String ttMajor
    );
}
