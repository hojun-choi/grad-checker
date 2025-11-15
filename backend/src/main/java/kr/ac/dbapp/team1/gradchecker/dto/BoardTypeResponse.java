package kr.ac.dbapp.team1.gradchecker.dto;

import kr.ac.dbapp.team1.gradchecker.domain.BoardType;
import lombok.Builder;
import lombok.Getter;

@Getter
@Builder
public class BoardTypeResponse {
    private Long boardTypeId;
    private String boardName;

    public static BoardTypeResponse from(BoardType boardType) {
        return BoardTypeResponse.builder()
                .boardTypeId(boardType.getId())
                .boardName(boardType.getBoardName())
                .build();
    }
}