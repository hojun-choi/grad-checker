package kr.ac.dbapp.team1.gradchecker.dto;

import kr.ac.dbapp.team1.gradchecker.domain.MajorHistory;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Getter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class MajorHistoryDto {

    private Long id;
    private Long currentMajorId;
    private String college;
    private String faculty;
    private String ttMajor;
    private String majorName;
    private String category;

    public static MajorHistoryDto from(MajorHistory entity) {
        return MajorHistoryDto.builder()
                .id(entity.getId())
                .currentMajorId(entity.getCurrentMajorId())
                .college(entity.getCollege())
                .faculty(entity.getFaculty())
                .ttMajor(entity.getTtMajor())
                .majorName(entity.getMajorName())
                .category(entity.getCategory())
                .build();
    }
}
