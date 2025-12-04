package kr.ac.dbapp.team1.gradchecker.repo;

import kr.ac.dbapp.team1.gradchecker.domain.MajorHistory;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface MajorHistoryRepository extends JpaRepository<MajorHistory, Long> {

    // year + category + is_deleted = false 인 row만 조회
    List<MajorHistory> findByYearAndCategoryAndIsDeletedFalse(int year, String category);
}
