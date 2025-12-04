package kr.ac.dbapp.team1.gradchecker.web;

import kr.ac.dbapp.team1.gradchecker.dto.MajorHistoryDto;
import kr.ac.dbapp.team1.gradchecker.domain.MajorHistory;
import kr.ac.dbapp.team1.gradchecker.repo.MajorHistoryRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequiredArgsConstructor
@RequestMapping("/api/majors")
public class MajorHistoryController {

    private final MajorHistoryRepository majorHistoryRepository;

    /**
     * 프론트: GET /majors/history?year=2025&category=학부전공
     */
    @GetMapping("/history")
    public List<MajorHistoryDto> getMajorHistory(
            @RequestParam int year,
            @RequestParam String category
    ) {
        List<MajorHistory> rows =
                majorHistoryRepository.findByYearAndCategoryAndIsDeletedFalse(year, category);

        return rows.stream()
                .map(MajorHistoryDto::from)
                .toList();
    }
}
