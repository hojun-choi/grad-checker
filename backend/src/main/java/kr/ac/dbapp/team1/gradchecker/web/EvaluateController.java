package kr.ac.dbapp.team1.gradchecker.web;

import jakarta.validation.Valid;
import kr.ac.dbapp.team1.gradchecker.dto.*;
import kr.ac.dbapp.team1.gradchecker.service.EvaluationService;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/evaluate")
public class EvaluateController {

  private final EvaluationService service;

  public EvaluateController(EvaluationService s){ this.service = s; }

  @PostMapping
  public EvaluateResult evaluate(@Valid @RequestBody EvaluateRequest req) {
    return service.evaluateByStudentNo(req.studentNo());
  }
}
