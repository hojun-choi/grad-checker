package kr.ac.dbapp.team1.gradchecker.dto;

import lombok.Getter;
import lombok.Setter;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;

@Getter
@Setter
public class PostSearchRequest {

    // 필터링 조건
    private String boardName; // 게시판 종류 이름

    // 검색 조건
    private String keyword;
    private String searchType; // 예: title, author

    // 정렬 조건
    private String sortBy = "latest"; // 기본값: 최신순 (latest)

    // 페이지
    private int page = 0; // 페이지 번호 (0부터 시작)
    private int size = 10; // 페이지당 개수

    public Pageable toPageable() {
        Sort sort;
        if ("views".equalsIgnoreCase(sortBy)) {
            // 조회순 정렬: viewCount 내림차순, 동일할 경우 createdAt 내림차순
            sort = Sort.by(Sort.Direction.DESC, "viewCount").and(Sort.by(Sort.Direction.DESC, "createdAt"));
        } else {
            // 최신순 정렬 (기본): createdAt 내림차순
            sort = Sort.by(Sort.Direction.DESC, "createdAt");
        }

        return PageRequest.of(page, size, sort);
    }
}