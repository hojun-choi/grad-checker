// src/main/java/kr/ac/dbapp/team1/gradchecker/repo/CommentRepository.java
package kr.ac.dbapp.team1.gradchecker.repo;

import kr.ac.dbapp.team1.gradchecker.domain.Comment;
import kr.ac.dbapp.team1.gradchecker.domain.Post;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional;

public interface CommentRepository extends JpaRepository<Comment, Long> {

    // CommentService 에서 사용하는 메서드
    Optional<Comment> findByIdAndIsDeletedFalse(Long id);

    // PostService.getPostById() 에서 댓글 리스트 조회용
    List<Comment> findByPostAndIsDeletedFalseOrderByCreatedAtAsc(Post post);
}
