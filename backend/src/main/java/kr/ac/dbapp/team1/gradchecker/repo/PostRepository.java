// src/main/java/kr/ac/dbapp/team1/gradchecker/repo/PostRepository.java
package kr.ac.dbapp.team1.gradchecker.repo;

import kr.ac.dbapp.team1.gradchecker.domain.Post;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.Optional;

public interface PostRepository extends JpaRepository<Post, Long> {

    // PostService / CommentService 에서 쓰는 메서드
    Optional<Post> findByIdAndIsDeletedFalse(Long id);

    /**
     * 게시글 검색 + 정렬 + 페이징
     *  - boardName: 게시판 필터 (nullable)
     *  - keyword  : 제목/내용 키워드 (nullable)
     *
     *  lower() 때문에 Hibernate 가 터졌으니까,
     *  그냥 LIKE 로만 검색하고, MySQL collation(utf8mb4_0900_ai_ci) 의
     *  대소문자 무시 기능에 맡기자.
     */
    @Query("""
        SELECT p
        FROM Post p
        WHERE p.isDeleted = false
          AND (:boardName IS NULL OR p.boardType.boardName = :boardName)
          AND (
                :keyword IS NULL
                OR p.title  LIKE concat('%', :keyword, '%')
                OR p.content LIKE concat('%', :keyword, '%')
              )
        """)
    Page<Post> search(
            @Param("boardName") String boardName,
            @Param("keyword")   String keyword,
            Pageable pageable
    );
}
