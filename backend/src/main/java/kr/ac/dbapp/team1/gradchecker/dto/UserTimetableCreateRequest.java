// src/main/java/kr/ac/dbapp/team1/gradchecker/dto/UserTimetableCreateRequest.java
package kr.ac.dbapp.team1.gradchecker.dto;

import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
public class UserTimetableCreateRequest {

    private Integer year;
    private String semester;
    private String name;
}
