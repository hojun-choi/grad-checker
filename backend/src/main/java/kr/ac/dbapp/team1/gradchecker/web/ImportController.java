package kr.ac.dbapp.team1.gradchecker.web;

import jakarta.transaction.Transactional;
import jakarta.validation.constraints.NotBlank;
import kr.ac.dbapp.team1.gradchecker.domain.*;
import kr.ac.dbapp.team1.gradchecker.repo.*;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.*;

import java.util.*;

@RestController
@RequestMapping("/api/import")
public class ImportController {

  private final StudentRepository studentRepo;
  private final TakenCourseRepository takenRepo;

  public ImportController(StudentRepository s, TakenCourseRepository t) {
    this.studentRepo = s; this.takenRepo = t;
  }

  public record TakenRow(@NotBlank String studentNo, @NotBlank String courseCode, @NotBlank String grade, @NotBlank String term){}

  @PostMapping(value="/taken", consumes = MediaType.APPLICATION_JSON_VALUE)
  @Transactional
  public Map<String,Object> importJson(@RequestBody List<TakenRow> rows) {
    var grouped = new HashMap<String, List<TakenRow>>();
    for (var r : rows) grouped.computeIfAbsent(r.studentNo, k->new ArrayList<>()).add(r);

    int inserted = 0;
    for (var e : grouped.entrySet()) {
      var st = studentRepo.findByStudentNo(e.getKey()).orElseThrow();
      for (var r : e.getValue()) {
        var tc = TakenCourse.builder().student(st).courseCode(r.courseCode()).grade(r.grade()).term(r.term()).build();
        takenRepo.save(tc); inserted++;
      }
    }
    return Map.of("status","ok","inserted",inserted);
  }
}
