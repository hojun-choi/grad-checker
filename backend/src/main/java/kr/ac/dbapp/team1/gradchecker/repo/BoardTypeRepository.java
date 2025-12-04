// src/main/java/kr/ac/dbapp/team1/gradchecker/repo/BoardTypeRepository.java
package kr.ac.dbapp.team1.gradchecker.repo;

import kr.ac.dbapp.team1.gradchecker.domain.BoardType;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional;

public interface BoardTypeRepository extends JpaRepository<BoardType, Long> {

    List<BoardType> findAllByIsDeletedFalseOrderByIdAsc();

    Optional<BoardType> findByBoardNameAndIsDeletedFalse(String boardName);
}
