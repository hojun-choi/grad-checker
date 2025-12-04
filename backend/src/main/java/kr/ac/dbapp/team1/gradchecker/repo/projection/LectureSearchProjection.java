// src/main/java/kr/ac/dbapp/team1/gradchecker/repo/projection/LectureSearchProjection.java
package kr.ac.dbapp.team1.gradchecker.repo.projection;

import java.sql.Time;

public interface LectureSearchProjection {

    Long getId();
    int getYear();
    String getSemester();

    String getCourseCode();
    String getCourseTitle();
    String getSectionNo();
    String getInstructorName();

    double getCourseCredits();
    double getLectureHours();
    int getCapacity();
    int getEnrolledCount();

    // ===== 여기부터는 lecture_schedule 에서 가져오는 값 =====
    String getMeetingDay();   // lecture_schedule.meeting_day
    Time getStartTime();      // lecture_schedule.start_time
    Time getEndTime();        // lecture_schedule.end_time
    String getBuildingRoom(); // lecture_schedule.building_room
}
