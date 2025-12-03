package kr.ac.dbapp.team1.gradchecker.service;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import kr.ac.dbapp.team1.gradchecker.domain.RagLog;
import kr.ac.dbapp.team1.gradchecker.domain.RagReference;
import kr.ac.dbapp.team1.gradchecker.dto.RagQueryRequest;
import kr.ac.dbapp.team1.gradchecker.repo.RagLogRepository;
import kr.ac.dbapp.team1.gradchecker.repo.RagReferenceRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.time.LocalDate;
import java.util.*;

import static java.util.Map.entry;

@Service
@RequiredArgsConstructor
public class RagService {

    // application.yml에서 설정 가능, 없으면 기본값 사용
    @Value("${rag.base-url:http://127.0.0.1:8000}")
    private String ragBaseUrl;

    private final RestTemplate restTemplate;
    private final ObjectMapper objectMapper;
    private final RagLogRepository ragLogRepository;
    private final RagReferenceRepository ragReferenceRepository;

    /**
     * 한글 학과 키워드 -> RAG department 토큰 매핑
     * (네가 준 파이썬 config 기준)
     */
    private static final Map<String, String> DEPT_KEYWORD_TO_TOKEN = Map.ofEntries(
            // 인문계열
            entry("기독교학과", "christian_studies"),
            entry("국어국문학과", "korean_language"),
            entry("중어중문학과", "chinese_language"),
            entry("영어영문학과", "english_language"),
            entry("영화예술학과", "film_arts"),
            entry("영화학과", "film_arts"),
            entry("불어불문학과", "french_language"),
            entry("독어독문학과", "german_language"),
            entry("사학과", "history"),
            entry("일어일문학과", "japanese_language"),
            entry("철학과", "philosophy"),
            entry("체육학과", "sports"),

            // 자연대
            entry("수학과", "mathematics"),
            entry("물리학과", "physics"),
            entry("화학과", "chemistry"),
            entry("통계학과", "statistics"),
            entry("생명과학과", "biomedical_science"),

            // 공대 / IT
            entry("화학공학과", "chemical"),
            entry("산업·정보시스템공학과", "industrial"),
            entry("산업정보시스템공학과", "industrial"),
            entry("산업정보시스템", "industrial"),

            entry("전기공학부", "electrical"),
            entry("기계공학부", "mechanical"),
            entry("건축학부", "architecture"),
            entry("신소재공학과", "material"),

            entry("소프트웨어학부", "software"),
            entry("소프트웨어학과", "software"),
            entry("소프트웨어", "software"),

            entry("컴퓨터학부", "computer"),
            entry("컴퓨터학과", "computer"),

            entry("글로벌미디어학부", "global_media"),
            entry("글로벌미디어", "global_media"),

            entry("ai융합학부", "ai_convergence"),
            entry("인공지능융합학부", "ai_convergence"),

            entry("정보보호학과", "infosec"),

            entry("차세대반도체공학과", "next_gen_semiconductor"),
            entry("자유전공학부", "liberal_study"),
            entry("베어드학부대학", "baird"),

            // 법/사회/경영
            entry("국제법무학과", "globallaw"),
            entry("법학과", "law"),
            entry("사회복지학부", "socialwelfare"),
            entry("행정학부", "publicadministration"),
            entry("정치외교학과", "politicalscience_internationalrelations"),
            entry("정보사회학과", "informationsociology"),
            entry("언론홍보학과", "journalism_publicrelation_advertising"),
            entry("평생교육학과", "lifelong_edu"),

            entry("경제학과", "economics"),
            entry("글로벌통상학과", "global_commerce"),
            entry("금융경제학과", "ecofinance"),
            entry("국제무역학과", "internationaltrade_transaction"),

            entry("경영학부", "business_administration"),
            entry("벤처중소기업학과", "venture_smallbusiness"),
            entry("회계학부", "accounting"),
            entry("금융학부", "finance"),
            entry("벤처경영학과", "venture_management"),
            entry("혁신경영학과", "innovation_management"),
            entry("복지경영학과", "welfare_management"),
            entry("회계세무학과", "accounting_tex"),

            // 학교 전체 학사공지
            entry("학교공지", "ssu"),
            entry("학사공지", "ssu"),
            entry("학사안내", "ssu"),
            entry("u-saint", "ssu"),
            entry("u saint", "ssu")
    );

    /**
     * 1) 쿼리에서 학과 키워드 찾아 dept 토큰 붙여서 FastAPI 호출
     * 2) 응답을 rag_logs / rag_references 에 저장
     * 3) FastAPI 응답 JSON을 그대로 리턴
     */
    public JsonNode queryAndLog(Long userId, RagQueryRequest request) {
        String originalQuery = request.getQuery();
        String expandedQuery = expandQueryWithDeptTokens(originalQuery);

        // FastAPI로 보낼 body
        ObjectNode body = objectMapper.createObjectNode();
        body.put("query", expandedQuery);
        body.put("top_k", request.getTopK() != null ? request.getTopK() : 10);

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);

        HttpEntity<String> httpEntity =
                new HttpEntity<>(body.toString(), headers);

        ResponseEntity<JsonNode> response = restTemplate.exchange(
                ragBaseUrl + "/rag/query",  // 최종: http://127.0.0.1:8000/rag/query
                HttpMethod.POST,
                httpEntity,
                JsonNode.class
        );

        JsonNode resBody = response.getBody();
        if (!response.getStatusCode().is2xxSuccessful() || resBody == null) {
            throw new RuntimeException("RAG 서버 응답 오류");
        }

        // =======================
        // rag_logs 저장
        // =======================
        String answer = resBody.path("answer").asText("");

        RagLog ragLog = RagLog.builder()
                .userId(userId)          // 지금은 null로 둬도 됨
                .question(originalQuery) // 사용자가 실제로 입력한 원본 쿼리
                .answer(answer)
                .build();

        ragLogRepository.save(ragLog);

        // =======================
        // rag_references 저장
        // =======================
        JsonNode docsNode = resBody.path("docs");
        if (docsNode.isArray()) {
            List<RagReference> refs = new ArrayList<>();

            for (JsonNode docNode : docsNode) {
                JsonNode meta = docNode.path("metadata");

                String title = meta.path("title").asText(null);
                String department = meta.path("department").asText(null);
                String link = meta.path("link").asText(null);
                String dateStr = meta.path("date").asText(null);

                if (title == null || link == null) {
                    continue;
                }

                LocalDate publishedDate = null;
                if (dateStr != null && !dateStr.isBlank()) {
                    try {
                        // RAG에서 YYYY-MM-DD 형식으로 주고 있으니까 그대로 파싱
                        publishedDate = LocalDate.parse(dateStr);
                    } catch (Exception ignored) {}
                }

                Double rrfScore = docNode.hasNonNull("rrf_score")
                        ? docNode.get("rrf_score").asDouble()
                        : null;
                Double combinedScore = docNode.hasNonNull("combined_score")
                        ? docNode.get("combined_score").asDouble()
                        : null;
                Double recencyScore = docNode.hasNonNull("recency_score")
                        ? docNode.get("recency_score").asDouble()
                        : null;

                RagReference ref = RagReference.builder()
                        .ragLog(ragLog)
                        .title(title)
                        .department(department)
                        .link(link)
                        .publishedDate(publishedDate)
                        .rrfScore(rrfScore)
                        .combinedScore(combinedScore)
                        .recencyScore(recencyScore)
                        .build();

                refs.add(ref);
            }

            if (!refs.isEmpty()) {
                ragReferenceRepository.saveAll(refs);
            }
        }

        // 프론트에는 FastAPI 결과 그대로 내려줌
        return resBody;
    }

    /**
     * 쿼리에서 학과 한글 키워드를 찾아서
     * "소프트웨어학부 전과 신청" ->
     * "소프트웨어학부 전과 신청 software"
     * 이런 식으로 토큰을 덧붙인다.
     */
    private String expandQueryWithDeptTokens(String original) {
        if (original == null || original.isBlank()) {
            return original;
        }

        String compact = original.replaceAll("\\s+", "").toLowerCase();
        Set<String> extraTokens = new LinkedHashSet<>();

        for (Map.Entry<String, String> e : DEPT_KEYWORD_TO_TOKEN.entrySet()) {
            String k = e.getKey().replaceAll("\\s+", "").toLowerCase();
            if (compact.contains(k)) {
                extraTokens.add(e.getValue());
            }
        }

        if (extraTokens.isEmpty()) {
            return original;
        }

        return original + " " + String.join(" ", extraTokens);
    }
}
