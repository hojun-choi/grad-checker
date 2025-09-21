package kr.ac.dbapp.team1.gradchecker.repo;

import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;
import kr.ac.dbapp.team1.gradchecker.domain.TakenCourse;

public interface TakenCourseRepository extends JpaRepository<TakenCourse, Long> {
  List<TakenCourse> findByStudentId(Long studentId);
}
