// src/main/java/kr/ac/dbapp/team1/gradchecker/dto/LectureDto.java
package kr.ac.dbapp.team1.gradchecker.dto;

import kr.ac.dbapp.team1.gradchecker.repo.projection.LectureSearchProjection;
import lombok.Builder;
import lombok.Getter;

@Getter
@Builder
public class LectureDto {

    private Long id;
    private int year;
    private String semester;

    private String courseCode;
    private String courseTitle;
    private String sectionNo;
    private String instructorName;

    private double courseCredits;
    private double lectureHours;
    private int capacity;
    private int enrolledCount;

    // 시간표 표시용
    private String meetingDay;   // "월" 같은 요일
    private String startTime;    // "13:30"
    private String endTime;      // "14:45"
    private String buildingRoom; // "형남공학관 123호"

    public static LectureDto fromProjection(LectureSearchProjection p) {
        return LectureDto.builder()
                .id(p.getId())
                .year(p.getYear())
                .semester(p.getSemester())
                .courseCode(p.getCourseCode())
                .courseTitle(p.getCourseTitle())
                .sectionNo(p.getSectionNo())
                .instructorName(p.getInstructorName())
                .courseCredits(p.getCourseCredits())
                .lectureHours(p.getLectureHours())
                .capacity(p.getCapacity())
                .enrolledCount(p.getEnrolledCount())
                .meetingDay(p.getMeetingDay())
                .startTime(p.getStartTime() != null ? p.getStartTime().toString().substring(0, 5) : null)
                .endTime(p.getEndTime() != null ? p.getEndTime().toString().substring(0, 5) : null)
                .buildingRoom(p.getBuildingRoom())
                .build();
    }
}
