// src/main/java/kr/ac/dbapp/team1/gradchecker/dto/PostSearchRequest.java
package kr.ac.dbapp.team1.gradchecker.dto;

import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
public class PostSearchRequest {

    // Board/index.vue에서 보내는 쿼리: page, size, sortBy, boardName, keyword

    private int page = 0;
    private int size = 20;
    private String sortBy = "latest";   // latest, popular

    private String boardName;           // 선택한 게시판명 (nullable)
    private String keyword;             // 검색어 (nullable)
}