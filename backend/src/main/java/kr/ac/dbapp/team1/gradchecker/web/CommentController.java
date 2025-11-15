package kr.ac.dbapp.team1.gradchecker.web;

import kr.ac.dbapp.team1.gradchecker.dto.CommentRequest;
import kr.ac.dbapp.team1.gradchecker.service.CommentService;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;
import jakarta.validation.Valid;

/**
 * 댓글 CRUD API 엔드포인트를 처리하는 컨트롤러입니다.
 */
@RestController
@RequestMapping("/api/board")
public class CommentController {

    private final CommentService commentService;

    public CommentController(CommentService commentService) {
        this.commentService = commentService;
    }

    // --- [ ] 댓글 작성 api 구현 ---
    /**
     * 특정 게시글에 댓글을 작성합니다.
     * URL: POST /api/board/posts/{postId}/comments
     */
    @PostMapping("/posts/{postId}/comments")
    public ResponseEntity<Long> createComment(
            @PathVariable Long postId,
            @Valid @RequestBody CommentRequest request,
            @AuthenticationPrincipal Long authenticatedUserId){

        Long newCommentId = commentService.createComment(postId, request, authenticatedUserId);

        return ResponseEntity.status(HttpStatus.CREATED).body(newCommentId);
    }

    // --- [ ] 댓글 수정 api 구현 ---
    /**
     * 댓글을 수정합니다.
     * URL: PUT /api/board/comments/{commentId}
     */
    @PutMapping("/comments/{commentId}")
    public ResponseEntity<Void> updateComment(
            @PathVariable Long commentId,
            @Valid @RequestBody CommentRequest request,
            @AuthenticationPrincipal Long authenticatedUserId) {

        commentService.updateComment(commentId, request, authenticatedUserId);

        return ResponseEntity.status(HttpStatus.NO_CONTENT).build();
    }

    // --- [ ] 댓글 삭제 api 구현 ---
    /**
     * 댓글을 삭제합니다.
     * URL: DELETE /api/board/comments/{commentId}
     */
    @DeleteMapping("/comments/{commentId}")
    public ResponseEntity<Void> deleteComment(
            @PathVariable Long commentId,
            @AuthenticationPrincipal Long authenticatedUserId) {
        commentService.deleteComment(commentId, authenticatedUserId);

        return ResponseEntity.status(HttpStatus.NO_CONTENT).build();
    }
}
