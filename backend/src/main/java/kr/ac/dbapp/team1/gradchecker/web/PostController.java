package kr.ac.dbapp.team1.gradchecker.web;

import kr.ac.dbapp.team1.gradchecker.dto.PostRequest;
import kr.ac.dbapp.team1.gradchecker.dto.PostResponse;
import kr.ac.dbapp.team1.gradchecker.dto.PostSearchRequest;
import kr.ac.dbapp.team1.gradchecker.service.PostService;
import org.springframework.data.domain.Page;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;
import jakarta.validation.Valid;
import java.util.NoSuchElementException;

//게시글 CRUD 및 목록 조회 API
@RestController
@RequestMapping("/api/board/posts") // 최종 확정된 URL 경로 사용
public class PostController {

    private final PostService postService;

    public PostController(PostService postService) {
        this.postService = postService;
    }

    // 예외 처리 핸들러 추가
    @ResponseStatus(HttpStatus.NOT_FOUND)
    @ExceptionHandler(NoSuchElementException.class)
    public String handleNotFound(NoSuchElementException e) {
        return e.getMessage();
    }

    // 권한 오류 처리 핸들러
    @ResponseStatus(HttpStatus.FORBIDDEN)
    @ExceptionHandler(ResponseStatusException.class)
    public String handleForbidden(ResponseStatusException e) {
        return e.getReason();
    }

    //글 작성 api
    @PostMapping
    public ResponseEntity<Long> createPost(@Valid @RequestBody PostRequest request) {
        Long authenticatedUserId = 1L;


        Long postId = postService.createPost(request, authenticatedUserId);
        // 생성 성공 시 201 CREATED 상태 코드 + ID
        return ResponseEntity.status(HttpStatus.CREATED).body(postId);
    }

    //글 조회 api
    @GetMapping("/{postId}")
    public ResponseEntity<PostResponse> getPostById(@PathVariable Long postId) {
        PostResponse response = postService.getPostById(postId);
        // 조회 성공 시 - 200ok
        return ResponseEntity.ok(response);
    }
    //글 수정 api
    @PutMapping("/{postId}")
    public ResponseEntity<Void> updatePost(
            @PathVariable Long postId,
            @Valid @RequestBody PostRequest request,
            @AuthenticationPrincipal Long authenticatedUserId) {

        postService.updatePost(postId, request, authenticatedUserId);
        return ResponseEntity.status(HttpStatus.NO_CONTENT).build();
    }

    //글 삭제 api 구현
    @DeleteMapping("/{postId}")
    public ResponseEntity<Void> deletePost(
            @PathVariable Long postId,
            @AuthenticationPrincipal Long authenticatedUserId) {

        postService.deletePost(postId, authenticatedUserId);
        return ResponseEntity.status(HttpStatus.NO_CONTENT).build();
    }

    //메인 화면 복합 조회 API구현
    @GetMapping("/search")
    public ResponseEntity<Page<PostResponse>> searchPosts(@ModelAttribute PostSearchRequest searchRequest) {
        Page<PostResponse> responsePage = postService.searchPosts(searchRequest);
        return ResponseEntity.ok(responsePage);
    }
}
