package kr.ac.dbapp.team1.gradchecker.web;

import com.fasterxml.jackson.databind.JsonNode;
import kr.ac.dbapp.team1.gradchecker.dto.RagQueryRequest;
import kr.ac.dbapp.team1.gradchecker.service.RagService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/rag")
@RequiredArgsConstructor
public class RagController {

    private final RagService ragService;

    @PostMapping("/query")
    public ResponseEntity<JsonNode> query(@RequestBody RagQueryRequest request) {
        // TODO: 로그인 붙이면 SecurityContext 등에서 userId 꺼내서 넣기
        Long userId = null;

        JsonNode result = ragService.queryAndLog(userId, request);
        return ResponseEntity.ok(result);
    }
}
