package kr.ac.dbapp.team1.gradchecker.web;

import jakarta.validation.Valid;
import kr.ac.dbapp.team1.gradchecker.dto.*;
import kr.ac.dbapp.team1.gradchecker.service.BoardTypeService;
import kr.ac.dbapp.team1.gradchecker.service.CommentService;
import kr.ac.dbapp.team1.gradchecker.service.PostService;
import org.springframework.data.domain.Page;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;

import java.util.List;
import java.util.NoSuchElementException;

@RestController
@RequestMapping("/api/board")
public class BoardController {

    private final PostService postService;
    private final BoardTypeService boardTypeService;
    private final CommentService commentService;

    public BoardController(PostService postService,
                           BoardTypeService boardTypeService,
                           CommentService commentService) {
        this.postService = postService;
        this.boardTypeService = boardTypeService;
        this.commentService = commentService;
    }

    // ================= 예외 처리 =================
    @ResponseStatus(HttpStatus.NOT_FOUND)
    @ExceptionHandler(NoSuchElementException.class)
    public String handleNotFound(NoSuchElementException e) {
        return e.getMessage();
    }

    @ResponseStatus(HttpStatus.FORBIDDEN)
    @ExceptionHandler(ResponseStatusException.class)
    public String handleForbidden(ResponseStatusException e) {
        return e.getReason();
    }

    // ================= 게시글 관련 =================

    @PostMapping("/posts")
    public ResponseEntity<Long> createPost(
            @Valid @RequestBody PostRequest request,
            @AuthenticationPrincipal(expression = "userId") Long authenticatedUserId
    ) {
        // 로그인 안된 경우(null) 처리: 실제 서비스에선 401 에러를 뱉거나 해야 함
        // 여기서는 테스트를 위해 1L로 고정하거나 예외 던짐
        Long userId = (authenticatedUserId != null) ? authenticatedUserId : 1L;

        Long postId = postService.createPost(request, userId);
        return ResponseEntity.status(HttpStatus.CREATED).body(postId);
    }

    @GetMapping("/posts")
    public ResponseEntity<PostListResponse> getAllPosts(@ModelAttribute PostSearchRequest searchRequest) {
        // 프론트에서 게시판 종류만 가져오기 위해 size=0을 보낼 때가 있음
        Page<PostResponse> responsePage = postService.searchPosts(searchRequest);
        
        // 게시판 종류 목록은 항상 같이 내려줌 (헤더 필터 및 글쓰기 카테고리용)
        List<BoardTypeResponse> boardTypes = boardTypeService.getAllBoardTypes();
        
        return ResponseEntity.ok(PostListResponse.of(responsePage, boardTypes));
    }

    @GetMapping("/posts/{postId}")
    public ResponseEntity<PostResponse> getPostById(
            @PathVariable Long postId,
            @AuthenticationPrincipal(expression = "userId") Long authenticatedUserId
    ) {
        // 비로그인 유저도 글은 볼 수 있으므로 null 허용
        Long userId = (authenticatedUserId != null) ? authenticatedUserId : null;

        PostResponse response = postService.getPostById(postId, userId);
        return ResponseEntity.ok(response);
    }

    @PutMapping("/posts/{postId}")
    public ResponseEntity<Void> updatePost(
            @PathVariable Long postId,
            @Valid @RequestBody PostRequest request,
            @AuthenticationPrincipal(expression = "userId") Long authenticatedUserId
    ) {
        Long userId = (authenticatedUserId != null) ? authenticatedUserId : 1L;
        postService.updatePost(postId, request, userId);
        return ResponseEntity.noContent().build();
    }

    @DeleteMapping("/posts/{postId}")
    public ResponseEntity<Void> deletePost(
            @PathVariable Long postId,
            @AuthenticationPrincipal(expression = "userId") Long authenticatedUserId
    ) {
        Long userId = (authenticatedUserId != null) ? authenticatedUserId : 1L;
        postService.deletePost(postId, userId);
        return ResponseEntity.noContent().build();
    }

    // ================= 댓글 관련 =================

    @PostMapping("/posts/{postId}/comments")
    public ResponseEntity<Long> createComment(
            @PathVariable Long postId,
            @Valid @RequestBody CommentRequest request,
            @AuthenticationPrincipal(expression = "userId") Long authenticatedUserId
    ) {
        Long userId = (authenticatedUserId != null) ? authenticatedUserId : 1L;
        Long newCommentId = commentService.createComment(postId, request, userId);
        return ResponseEntity.status(HttpStatus.CREATED).body(newCommentId);
    }

    @PutMapping("/comments/{commentId}")
    public ResponseEntity<Void> updateComment(
            @PathVariable Long commentId,
            @Valid @RequestBody CommentRequest request,
            @AuthenticationPrincipal(expression = "userId") Long authenticatedUserId
    ) {
        Long userId = (authenticatedUserId != null) ? authenticatedUserId : 1L;
        commentService.updateComment(commentId, request, userId);
        return ResponseEntity.noContent().build();
    }

    @DeleteMapping("/comments/{commentId}")
    public ResponseEntity<Void> deleteComment(
            @PathVariable Long commentId,
            @AuthenticationPrincipal(expression = "userId") Long authenticatedUserId
    ) {
        Long userId = (authenticatedUserId != null) ? authenticatedUserId : 1L;
        commentService.deleteComment(commentId, userId);
        return ResponseEntity.noContent().build();
    }
}