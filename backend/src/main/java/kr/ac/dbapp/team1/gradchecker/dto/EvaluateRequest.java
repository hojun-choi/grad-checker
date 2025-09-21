package kr.ac.dbapp.team1.gradchecker.dto;

import jakarta.validation.constraints.NotBlank;

public record EvaluateRequest(
  @NotBlank String studentNo
) {}
