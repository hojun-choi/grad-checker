// src/main/java/kr/ac/dbapp/team1/gradchecker/service/BoardTypeService.java
package kr.ac.dbapp.team1.gradchecker.service;

import kr.ac.dbapp.team1.gradchecker.domain.BoardType;
import kr.ac.dbapp.team1.gradchecker.dto.BoardTypeResponse;
import kr.ac.dbapp.team1.gradchecker.repo.BoardTypeRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class BoardTypeService {

    private final BoardTypeRepository boardTypeRepository;

    public List<BoardTypeResponse> getAllBoardTypes() {
        List<BoardType> types = boardTypeRepository.findAllByIsDeletedFalseOrderByIdAsc();
        return types.stream()
                .map(BoardTypeResponse::from)
                .toList();
    }

    @Transactional(readOnly = true)
    public BoardType getByBoardNameOrThrow(String boardName) {
        return boardTypeRepository.findByBoardNameAndIsDeletedFalse(boardName)
                .orElseThrow(() -> new IllegalArgumentException("존재하지 않는 게시판명입니다: " + boardName));
    }
}
