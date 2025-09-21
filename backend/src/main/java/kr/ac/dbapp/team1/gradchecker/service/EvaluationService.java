package kr.ac.dbapp.team1.gradchecker.service;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import java.util.*;
import java.util.stream.Collectors;
import kr.ac.dbapp.team1.gradchecker.domain.Course;
import kr.ac.dbapp.team1.gradchecker.domain.TakenCourse;
import kr.ac.dbapp.team1.gradchecker.domain.RequirementRule; // ★ 누락시 추가
import kr.ac.dbapp.team1.gradchecker.dto.EvaluateResult;
import kr.ac.dbapp.team1.gradchecker.repo.CourseRepository;
import kr.ac.dbapp.team1.gradchecker.repo.RequirementRuleRepository;
import kr.ac.dbapp.team1.gradchecker.repo.StudentRepository;
import kr.ac.dbapp.team1.gradchecker.repo.TakenCourseRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@Transactional(readOnly = true)
public class EvaluationService {

  private final StudentRepository studentRepo;
  private final TakenCourseRepository takenRepo;
  private final CourseRepository courseRepo;
  private final RequirementRuleRepository ruleRepo;
  private final ObjectMapper om = new ObjectMapper();

  public EvaluationService(
      StudentRepository s,
      TakenCourseRepository t,
      CourseRepository c,
      RequirementRuleRepository r) {
    this.studentRepo = s;
    this.takenRepo = t;
    this.courseRepo = c;
    this.ruleRepo = r;
  }

  public EvaluateResult evaluateByStudentNo(String studentNo) {
    // ----- 레포 호출 결과를 명시적 타입으로 -----
    var student = studentRepo.findByStudentNo(studentNo).orElseThrow();

    List<TakenCourse> taken = takenRepo.findByStudentId(student.getId());                  // ★
    Set<String> codes = taken.stream().map(TakenCourse::getCourseCode).collect(Collectors.toSet());

    Map<String, Course> courseMap = courseRepo.findByCodeIn(codes).stream()               // ★
        .collect(Collectors.toMap(Course::getCode, c -> c));

    List<RequirementRule> rules = ruleRepo.findByCatalogYear(student.getCatalogYear());   // ★

    int totalCredits = 0, majorCredits = 0, geCredits = 0;
    Map<String, Integer> geAreaCredits = new HashMap<>();

    // ----- for-each에도 명시 타입 -----
    for (TakenCourse tc : taken) {                                                         // ★
      Course c = courseMap.get(tc.getCourseCode());
      if (c == null) continue;
      int cr = c.getCredits();
      totalCredits += cr;
      switch (c.getType()) {
        case "MAJOR" -> majorCredits += cr;
        case "GE" -> {
          geCredits += cr;
          if (c.getGeArea() != null) {
            geAreaCredits.merge(c.getGeArea(), cr, Integer::sum);
          }
        }
        default -> {
          // FREE 등은 총학점만 카운트
        }
      }
    }

    int totalReq = 0, majorReq = 0, geReq = 0;
    List<String> geAreaShort = new ArrayList<>();
    List<String> missingCourses = new ArrayList<>();
    List<String> messages = new ArrayList<>();

    for (RequirementRule r : rules) {                                                     // ★
      String type = r.getRuleType();
      try {
        String json = r.getParamsJson();
        if (json == null || json.isBlank()) {
          messages.add("규칙 파싱 오류(빈 params_json): " + r.getId());
          continue;
        }
        JsonNode node = om.readTree(json);

        switch (type) {
          case "CREDITS_AT_LEAST" -> {
            JsonNode creditsNode = node.get("credits");
            if (creditsNode == null || !creditsNode.isInt()) {
              messages.add("규칙 형식 오류(CREDITS_AT_LEAST): credits 정수 아님, ruleId=" + r.getId());
              break;
            }
            int req = creditsNode.asInt();
            switch (r.getGroupCode()) {
              case "TOTAL" -> totalReq = Math.max(totalReq, req);
              case "MAJOR" -> majorReq = Math.max(majorReq, req);
              case "GE"    -> geReq    = Math.max(geReq, req);
              default -> messages.add("알 수 없는 groupCode: " + r.getGroupCode());
            }
          }

          case "GE_AREA_AT_LEAST" -> {
            JsonNode areaNode = node.get("area");
            JsonNode creditsNode = node.get("credits");
            if (areaNode == null || !areaNode.isTextual() || creditsNode == null || !creditsNode.isInt()) {
              messages.add("규칙 형식 오류(GE_AREA_AT_LEAST): area/text 또는 credits/int 누락, ruleId=" + r.getId());
              break;
            }
            String area = areaNode.asText();
            int req = creditsNode.asInt();
            int have = geAreaCredits.getOrDefault(area, 0);
            if (have < req) geAreaShort.add(area + " 부족 " + (req - have) + "학점");
          }

          case "INCLUDE_COURSES" -> {
            JsonNode codesNode = node.get("codes");
            if (codesNode == null || !codesNode.isArray()) {
              messages.add("규칙 형식 오류(INCLUDE_COURSES): codes 배열 누락, ruleId=" + r.getId());
              break;
            }
            ArrayNode arr = (ArrayNode) codesNode;
            for (JsonNode n : arr) {
              String code = n.asText();
              if (!codes.contains(code)) missingCourses.add(code);
            }
          }

          default -> {
            // 알 수 없는 rule_type은 무시/로그
          }
        }

      } catch (Exception e) {
        messages.add("규칙 파싱 오류: " + r.getId());
      }
    }

    boolean ok = true;
    if (totalReq > 0 && totalCredits < totalReq) ok = false;
    if (majorReq > 0 && majorCredits < majorReq) ok = false;
    if (geReq > 0 && geCredits < geReq) ok = false;
    if (!geAreaShort.isEmpty()) ok = false;
    if (!missingCourses.isEmpty()) ok = false;

    return new EvaluateResult(
        ok,
        totalCredits,
        totalReq,
        majorCredits,
        majorReq,
        geCredits,
        geReq,
        geAreaShort,
        missingCourses,
        messages);
  }
}
