// src/main/java/kr/ac/dbapp/team1/gradchecker/service/CommentService.java
package kr.ac.dbapp.team1.gradchecker.service;

import kr.ac.dbapp.team1.gradchecker.domain.Comment;
import kr.ac.dbapp.team1.gradchecker.domain.Post;
import kr.ac.dbapp.team1.gradchecker.domain.User;
import kr.ac.dbapp.team1.gradchecker.dto.CommentRequest;
import kr.ac.dbapp.team1.gradchecker.repo.CommentRepository;
import kr.ac.dbapp.team1.gradchecker.repo.PostRepository;
import kr.ac.dbapp.team1.gradchecker.repo.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.server.ResponseStatusException;

import java.util.NoSuchElementException;

@Service
@RequiredArgsConstructor
public class CommentService {

    private final CommentRepository commentRepository;
    private final PostRepository postRepository;
    private final UserRepository userRepository;

    /**
     * 댓글 작성
     */
    @Transactional
    public Long createComment(Long postId, CommentRequest request, Long userId) {
        Post post = postRepository.findByIdAndIsDeletedFalse(postId)
                .orElseThrow(() -> new NoSuchElementException("게시글을 찾을 수 없습니다."));

        User user = userRepository.findById(userId)
                .orElseThrow(() -> new NoSuchElementException("사용자를 찾을 수 없습니다."));

        Comment parent = null;
        if (request.getParentCommentId() != null) {
            parent = commentRepository.findByIdAndIsDeletedFalse(request.getParentCommentId())
                    .orElseThrow(() -> new NoSuchElementException("부모 댓글을 찾을 수 없습니다."));
        }

        Comment comment = Comment.builder()
                .post(post)
                .user(user)
                .parentComment(parent)
                .content(request.getContent())
                .isAnonymous(request.isAnonymous())
                .isDeleted(false)
                .build();

        commentRepository.save(comment);
        post.increaseCommentCount();

        return comment.getId();
    }

    /**
     * 댓글 수정
     */
    @Transactional
    public void updateComment(Long commentId, CommentRequest request, Long userId) {
        Comment comment = commentRepository.findByIdAndIsDeletedFalse(commentId)
                .orElseThrow(() -> new NoSuchElementException("댓글을 찾을 수 없습니다."));

        // 🔐 작성자 본인 확인 (User.userId)
        if (!comment.getUser().getUserId().equals(userId)) {
            throw new ResponseStatusException(HttpStatus.FORBIDDEN, "본인이 작성한 댓글만 수정할 수 있습니다.");
        }

        comment.setContent(request.getContent());
        comment.setIsAnonymous(request.isAnonymous());
    }

    /**
     * 댓글 삭제 (soft delete)
     */
    @Transactional
    public void deleteComment(Long commentId, Long userId) {
        Comment comment = commentRepository.findByIdAndIsDeletedFalse(commentId)
                .orElseThrow(() -> new NoSuchElementException("댓글을 찾을 수 없습니다."));

        // 🔐 작성자 본인 확인
        if (!comment.getUser().getUserId().equals(userId)) {
            throw new ResponseStatusException(HttpStatus.FORBIDDEN, "본인이 작성한 댓글만 삭제할 수 있습니다.");
        }

        if (!Boolean.TRUE.equals(comment.getIsDeleted())) {
            comment.setIsDeleted(true);
            Post post = comment.getPost();
            post.decreaseCommentCount();
        }
    }
}