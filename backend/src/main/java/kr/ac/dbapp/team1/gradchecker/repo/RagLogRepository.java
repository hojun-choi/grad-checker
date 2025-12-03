package kr.ac.dbapp.team1.gradchecker.repo;

import kr.ac.dbapp.team1.gradchecker.domain.RagLog;
import org.springframework.data.jpa.repository.JpaRepository;

public interface RagLogRepository extends JpaRepository<RagLog, Long> {
}
