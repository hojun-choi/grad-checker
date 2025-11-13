// backend/src/main/java/kr/ac/dbapp/team1/gradchecker/dto/AuthResponse.java
package kr.ac.dbapp.team1.gradchecker.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.util.List;

@Getter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class AuthResponse {
    private String username;
    private List<String> roles;
    private String studentNo;
    private String departmentName;
    private String catalogYear;
}