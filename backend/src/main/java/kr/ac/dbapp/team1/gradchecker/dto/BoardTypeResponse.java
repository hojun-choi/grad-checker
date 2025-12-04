// src/main/java/kr/ac/dbapp/team1/gradchecker/dto/BoardTypeResponse.java
package kr.ac.dbapp.team1.gradchecker.dto;

import kr.ac.dbapp.team1.gradchecker.domain.BoardType;
import lombok.AllArgsConstructor;
import lombok.Getter;

@Getter
@AllArgsConstructor
public class BoardTypeResponse {

    private Long id;
    private String boardName;

    public static BoardTypeResponse from(BoardType bt) {
        return new BoardTypeResponse(bt.getId(), bt.getBoardName());
    }
}