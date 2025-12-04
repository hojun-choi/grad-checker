// src/main/java/kr/ac/dbapp/team1/gradchecker/dto/UserTimetableDto.java
package kr.ac.dbapp.team1.gradchecker.dto;

import kr.ac.dbapp.team1.gradchecker.domain.UserTimetable;
import lombok.Builder;
import lombok.Getter;

import java.util.List;

@Getter
@Builder
public class UserTimetableDto {

    private Long id;
    private Integer year;
    private String semester;
    private String name;
    private boolean isPrimary;
    private List<TimetableClassDto> classes;

    // 엔티티 + 우리가 만든 classes 를 함께 받아서 DTO로 변환
    public static UserTimetableDto fromEntity(UserTimetable tt,
                                              List<TimetableClassDto> classes) {
        return UserTimetableDto.builder()
                .id(tt.getId())
                .year(tt.getYear())
                .semester(tt.getSemester())
                .name(tt.getName())
                .isPrimary(tt.isMain())
                .classes(classes)
                .build();
    }
}