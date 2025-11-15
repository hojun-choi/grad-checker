package kr.ac.dbapp.team1.gradchecker.service;

import kr.ac.dbapp.team1.gradchecker.domain.Comment;
import kr.ac.dbapp.team1.gradchecker.dto.CommentRequest;
import kr.ac.dbapp.team1.gradchecker.repo.CommentRepository;
import kr.ac.dbapp.team1.gradchecker.repo.PostRepository;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.server.ResponseStatusException;

import java.util.NoSuchElementException;

/**
 * 댓글 작성, 수정, 삭제 비즈니스 로직을 처리하는 서비스입니다.
 */
@Service
public class CommentService {

    private final CommentRepository commentRepository;
    private final PostRepository postRepository;

    public CommentService(CommentRepository commentRepository, PostRepository postRepository) {
        this.commentRepository = commentRepository;
        this.postRepository = postRepository;
    }

    /**
     * @설명: 새로운 댓글을 저장하고, 게시글의 댓글 수를 1 증가시킵니다.
     * @API: [ ] 댓글 작성 api 구현
     */
    @Transactional
    public Long createComment(Long postId, CommentRequest request, Long authenticatedUserId) {
        // 1. 게시글 존재 여부 확인 (댓글이 달릴 게시글이 있어야 함)
        if (!postRepository.existsById(postId)) {
            throw new NoSuchElementException("댓글을 작성할 게시글을 찾을 수 없습니다.");
        }

        // 2. 댓글 엔티티 생성
        Comment newComment = Comment.builder()
                .postId(postId)
                .userId(authenticatedUserId)
                .content(request.getContent())
                .parentCommentId(request.getParentCommentId())
                .build();

        Comment savedComment = commentRepository.save(newComment);

        // 3. 비즈니스 로직: 게시글의 댓글 수 증가 (Post 엔티티에 로직 추가 필요)
        postRepository.findById(postId).ifPresent(post -> {
            post.incrementCommentCount(); // Post 엔티티에 구현된 메서드 사용
        });

        return savedComment.getId();
    }

    /**
     * @설명: 댓글을 수정합니다. (권한 확인 필수)
     * @API: [ ] 댓글 수정 api 구현
     */
    @Transactional
    public void updateComment(Long commentId, CommentRequest request, Long authenticatedUserId) {
        Comment comment = commentRepository.findById(commentId)
                .filter(c -> !c.isDeleted())
                .orElseThrow(() -> new NoSuchElementException("수정할 댓글을 찾을 수 없습니다."));

        // 권한 확인
        if (!comment.getUserId().equals(authenticatedUserId)) {
            throw new ResponseStatusException(HttpStatus.FORBIDDEN, "댓글을 수정할 권한이 없습니다.");
        }

        comment.update(request.getContent());
    }

    /**
     * @설명: 댓글을 논리적으로 삭제 처리합니다. (권한 확인 필수)
     * @API: [ ] 댓글 삭제 api 구현
     */
    @Transactional
    public void deleteComment(Long commentId, Long authenticatedUserId) {
        Comment comment = commentRepository.findById(commentId).orElse(null);

        if (comment == null || comment.isDeleted()) {
            throw new NoSuchElementException("삭제할 댓글을 찾을 수 없습니다.");
        }

        // 권한 확인
        if (!comment.getUserId().equals(authenticatedUserId)) {
            throw new ResponseStatusException(HttpStatus.FORBIDDEN, "댓글을 삭제할 권한이 없습니다.");
        }

        // 논리적 삭제
        comment.markAsDeleted();

        // 💡 비즈니스 로직: 게시글의 댓글 수 감소 (Post 엔티티에 로직 추가 필요)
        postRepository.findById(comment.getPostId()).ifPresent(post -> {
            post.decrementCommentCount();
        });
    }
}
