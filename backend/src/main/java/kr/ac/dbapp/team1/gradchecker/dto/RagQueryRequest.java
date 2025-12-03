package kr.ac.dbapp.team1.gradchecker.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;

@Data
public class RagQueryRequest {

    // 프론트에서 보내는 자연어 질문
    private String query;

    // JSON에서는 top_k, 자바에서는 topK
    @JsonProperty("top_k")
    private Integer topK;
}
