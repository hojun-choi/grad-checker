package kr.ac.dbapp.team1.gradchecker.web;

import kr.ac.dbapp.team1.gradchecker.dto.BoardTypeResponse;
import kr.ac.dbapp.team1.gradchecker.service.BoardTypeService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/api/board/types")
public class BoardTypeController {

    private final BoardTypeService boardTypeService;

    public BoardTypeController(BoardTypeService boardTypeService) {
        this.boardTypeService = boardTypeService;
    }

    /**
     * @설명: 모든 게시판 종류 목록을 반환합니다.
     * URL: GET /api/board/types
     */
    @GetMapping
    public ResponseEntity<List<BoardTypeResponse>> getBoardTypes() {
        List<BoardTypeResponse> response = boardTypeService.getAllBoardTypes();
        return ResponseEntity.ok(response);
    }
}