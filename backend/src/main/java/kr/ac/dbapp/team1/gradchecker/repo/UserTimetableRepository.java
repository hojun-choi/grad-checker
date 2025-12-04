// src/main/java/kr/ac/dbapp/team1/gradchecker/repo/UserTimetableRepository.java
package kr.ac.dbapp.team1.gradchecker.repo;

import kr.ac.dbapp.team1.gradchecker.domain.User;
import kr.ac.dbapp.team1.gradchecker.domain.UserTimetable;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional;

public interface UserTimetableRepository extends JpaRepository<UserTimetable, Long> {

    List<UserTimetable> findByUserAndYearAndSemester(User user, Integer year, String semester);

    Optional<UserTimetable> findByIdAndUser(Long id, User user);
}
