// src/main/java/kr/ac/dbapp/team1/gradchecker/dto/TimetableClassProjection.java
package kr.ac.dbapp.team1.gradchecker.dto;

public interface TimetableClassProjection {

    Long getLectureId();  // lecture_timetable.id
    Integer getDay();     // 0 ~ 4
    Double getStart();    // 9.0 같은 double
    Double getEnd();      // 10.5 같은 double
    String getName();     // 강의명
    String getRoom();     // 강의실
}