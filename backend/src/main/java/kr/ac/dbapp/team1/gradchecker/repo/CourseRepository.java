package kr.ac.dbapp.team1.gradchecker.repo;

import java.util.*;
import org.springframework.data.jpa.repository.JpaRepository;
import kr.ac.dbapp.team1.gradchecker.domain.Course;

public interface CourseRepository extends JpaRepository<Course, Long> {
  Optional<Course> findByCode(String code);
  List<Course> findByCodeIn(Collection<String> codes);
}
