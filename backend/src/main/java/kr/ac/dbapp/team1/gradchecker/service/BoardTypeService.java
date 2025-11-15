package kr.ac.dbapp.team1.gradchecker.service;

import kr.ac.dbapp.team1.gradchecker.domain.BoardType;
import kr.ac.dbapp.team1.gradchecker.dto.BoardTypeResponse;
import kr.ac.dbapp.team1.gradchecker.repo.BoardTypeRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.util.List;
import java.util.stream.Collectors;

//게시판 목록 조회
@Service
@Transactional(readOnly = true)
public class BoardTypeService {

    private final BoardTypeRepository boardTypeRepository;

    public BoardTypeService(BoardTypeRepository boardTypeRepository) {
        this.boardTypeRepository = boardTypeRepository;
    }

    //삭제 되지 않은 게시판 조회
    public List<BoardTypeResponse> getAllBoardTypes() {
        List<BoardType> boardTypes = boardTypeRepository.findByIsDeletedFalse();

        return boardTypes.stream()
                .map(BoardTypeResponse::from)
                .collect(Collectors.toList());
    }
}