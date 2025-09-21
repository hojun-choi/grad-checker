package kr.ac.dbapp.team1.gradchecker.repo;

import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;
import kr.ac.dbapp.team1.gradchecker.domain.RequirementRule;

public interface RequirementRuleRepository extends JpaRepository<RequirementRule, Long> {
  List<RequirementRule> findByCatalogYear(int catalogYear);
}
