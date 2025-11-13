package kr.ac.dbapp.team1.gradchecker.dto;

import jakarta.validation.constraints.NotBlank;

public record LoginRequest(
    @NotBlank String username,
    @NotBlank String password)
{}
