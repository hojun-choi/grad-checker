package kr.ac.dbapp.team1.gradchecker.repo;

import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;
import kr.ac.dbapp.team1.gradchecker.domain.Student;

public interface StudentRepository extends JpaRepository<Student, Long> {
  Optional<Student> findByStudentNo(String studentNo);
}
