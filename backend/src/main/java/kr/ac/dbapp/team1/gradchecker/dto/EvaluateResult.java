package kr.ac.dbapp.team1.gradchecker.dto;

import java.util.List;

public record EvaluateResult(
  boolean allSatisfied,
  int totalCredits, int totalRequired,
  int majorCredits, int majorRequired,
  int geCredits, int geRequired,
  List<String> geAreaShortages,
  List<String> missingCourses,
  List<String> messages
) {}
