package kr.ac.dbapp.team1.gradchecker.dto;

/**
 * 로그인 요청 DTO
 * 
 * 프론트에서 보내는 JSON:
 * {
 *   "loginId": "hojun123",
 *   "password": "pw123456"
 * }
 */
public record LoginRequest(
        String loginId,
        String password
) {}
