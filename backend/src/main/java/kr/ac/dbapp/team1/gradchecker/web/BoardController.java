// src/main/java/kr/ac/dbapp/team1/gradchecker/web/BoardController.java
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

/**
 * 게시글 + 댓글을 한 번에 처리하는 통합 컨트롤러
 *
 * base path: /api/board
 *
 * - 게시글 목록     : GET    /api/board/posts
 * - 게시글 단건     : GET    /api/board/posts/{postId}
 * - 게시글 작성     : POST   /api/board/posts
 * - 게시글 수정     : PUT    /api/board/posts/{postId}
 * - 게시글 삭제     : DELETE /api/board/posts/{postId}
 * - 검색            : GET    /api/board/posts/search
 *
 * - 댓글 작성       : POST   /api/board/posts/{postId}/comments
 * - 댓글 수정       : PUT    /api/board/comments/{commentId}
 * - 댓글 삭제       : DELETE /api/board/comments/{commentId}
 */
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

    /**
     * 게시글 작성
     * POST /api/board/posts
     */
    @PostMapping("/posts")
    public ResponseEntity<Long> createPost(
            @Valid @RequestBody PostRequest request,
            // TODO: 나중에 실제 로그인 유저에서 꺼내 쓰기
            @AuthenticationPrincipal(expression = "userId") Long authenticatedUserId
    ) {
        if (authenticatedUserId == null) {
            // 임시: 로그인 연동 전까지 1L로 고정 사용
            authenticatedUserId = 1L;
        }

        Long postId = postService.createPost(request, authenticatedUserId);
        return ResponseEntity.status(HttpStatus.CREATED).body(postId);
    }

    /**
     * 게시글 목록 조회
     * GET /api/board/posts?page=&size=&sortBy=
     */
    @GetMapping("/posts")
    public ResponseEntity<PostListResponse> getAllPosts(@ModelAttribute PostSearchRequest searchRequest) {
        Page<PostResponse> responsePage = postService.searchPosts(searchRequest);
        List<BoardTypeResponse> boardTypes = boardTypeService.getAllBoardTypes();
        return ResponseEntity.ok(PostListResponse.of(responsePage, boardTypes));
    }

    /**
     * 게시글 단건 조회
     * GET /api/board/posts/{postId}
     */
    @GetMapping("/posts/{postId}")
    public ResponseEntity<PostResponse> getPostById(@PathVariable Long postId) {
        PostResponse response = postService.getPostById(postId);
        return ResponseEntity.ok(response);
    }

    /**
     * 게시글 수정
     * PUT /api/board/posts/{postId}
     */
    @PutMapping("/posts/{postId}")
    public ResponseEntity<Void> updatePost(
            @PathVariable Long postId,
            @Valid @RequestBody PostRequest request,
            @AuthenticationPrincipal(expression = "userId") Long authenticatedUserId
    ) {
        if (authenticatedUserId == null) {
            authenticatedUserId = 1L;
        }
        postService.updatePost(postId, request, authenticatedUserId);
        return ResponseEntity.noContent().build();
    }

    /**
     * 게시글 삭제
     * DELETE /api/board/posts/{postId}
     */
    @DeleteMapping("/posts/{postId}")
    public ResponseEntity<Void> deletePost(
            @PathVariable Long postId,
            @AuthenticationPrincipal(expression = "userId") Long authenticatedUserId
    ) {
        if (authenticatedUserId == null) {
            authenticatedUserId = 1L;
        }
        postService.deletePost(postId, authenticatedUserId);
        return ResponseEntity.noContent().build();
    }

    /**
     * 게시글 검색
     * GET /api/board/posts/search
     */
    @GetMapping("/posts/search")
    public ResponseEntity<Page<PostResponse>> searchPosts(@ModelAttribute PostSearchRequest searchRequest) {
        Page<PostResponse> responsePage = postService.searchPosts(searchRequest);
        return ResponseEntity.ok(responsePage);
    }

    // ================= 댓글 관련 =================

    /**
     * 댓글 작성
     * POST /api/board/posts/{postId}/comments
     */
    @PostMapping("/posts/{postId}/comments")
    public ResponseEntity<Long> createComment(
            @PathVariable Long postId,
            @Valid @RequestBody CommentRequest request,
            @AuthenticationPrincipal(expression = "userId") Long authenticatedUserId
    ) {
        if (authenticatedUserId == null) {
            authenticatedUserId = 1L;
        }
        Long newCommentId = commentService.createComment(postId, request, authenticatedUserId);
        return ResponseEntity.status(HttpStatus.CREATED).body(newCommentId);
    }

    /**
     * 댓글 수정
     * PUT /api/board/comments/{commentId}
     */
    @PutMapping("/comments/{commentId}")
    public ResponseEntity<Void> updateComment(
            @PathVariable Long commentId,
            @Valid @RequestBody CommentRequest request,
            @AuthenticationPrincipal(expression = "userId") Long authenticatedUserId
    ) {
        if (authenticatedUserId == null) {
            authenticatedUserId = 1L;
        }
        commentService.updateComment(commentId, request, authenticatedUserId);
        return ResponseEntity.noContent().build();
    }

    /**
     * 댓글 삭제
     * DELETE /api/board/comments/{commentId}
     */
    @DeleteMapping("/comments/{commentId}")
    public ResponseEntity<Void> deleteComment(
            @PathVariable Long commentId,
            @AuthenticationPrincipal(expression = "userId") Long authenticatedUserId
    ) {
        if (authenticatedUserId == null) {
            authenticatedUserId = 1L;
        }
        commentService.deleteComment(commentId, authenticatedUserId);
        return ResponseEntity.noContent().build();
    }
}
