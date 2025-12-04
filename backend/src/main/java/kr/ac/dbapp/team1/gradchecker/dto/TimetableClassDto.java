// src/main/java/kr/ac/dbapp/team1/gradchecker/dto/TimetableClassDto.java
package kr.ac.dbapp.team1.gradchecker.dto;

import lombok.Builder;
import lombok.Getter;

@Getter
@Builder
public class TimetableClassDto {

    private Long id;      // lecture_timetable.id
    private Integer day;  // 0=월 ~ 4=금
    private double start; // 9.0
    private double end;   // 10.5
    private String name;  // 강의명
    private String room;  // 강의실

    // 네이티브 쿼리 결과를 DTO로 변환
    public static TimetableClassDto fromProjection(TimetableClassProjection p) {
        return TimetableClassDto.builder()
                .id(p.getLectureId())
                .day(p.getDay())
                .start(p.getStart())
                .end(p.getEnd())
                .name(p.getName())
                .room(p.getRoom())
                .build();
    }
}