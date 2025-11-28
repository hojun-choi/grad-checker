package kr.ac.dbapp.team1.gradchecker.domain;

import jakarta.persistence.*;
import lombok.AccessLevel;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Entity
@Table(name = "posts")
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class Post {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "post_id")
    private Long id;

    @Column(name = "user_id", nullable = false)
    private Long userId;

    /**
     * 게시판 종류 (공지, 졸업, 전과 등)를 나타내는 BoardType 엔티티와의 연관관계.
     * 실제 컬럼은 board_type_id 로 저장된다.
     */
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "board_type_id", nullable = false)
    private BoardType boardType;

    @Column(name = "title", nullable = false, length = 200)
    private String title;

    @Column(name = "content", nullable = false, columnDefinition = "MEDIUMTEXT")
    private String content;

    @Column(name = "comment_count", nullable = false)
    private int commentCount = 0;

    @Column(name = "view_count", nullable = false)
    private int viewCount = 0;

    @Column(name = "created_at", nullable = false)
    private LocalDateTime createdAt;

    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    @Column(name = "is_deleted", nullable = false)
    private boolean isDeleted = false;

    @Builder
    public Post(Long userId, BoardType boardType, String title, String content) {
        this.userId = userId;
        this.boardType = boardType;
        this.title = title;
        this.content = content;
        this.createdAt = LocalDateTime.now();
    }

    // 게시글 수정
    public void update(String title, String content, BoardType boardType) {
        this.title = title;
        this.content = content;
        this.boardType = boardType;
        this.updatedAt = LocalDateTime.now();
    }

    // 조회수 증가
    public void incrementViewCount() {
        this.viewCount += 1;
    }

    // 논리 삭제
    public void markAsDeleted() {
        this.isDeleted = true;
        this.updatedAt = LocalDateTime.now();
    }

    // 댓글 수 증가
    public void incrementCommentCount() {
        this.commentCount++;
        this.updatedAt = LocalDateTime.now();
    }

    // 댓글 수 감소
    public void decrementCommentCount() {
        if (this.commentCount > 0) {
            this.commentCount--;
        }
        this.updatedAt = LocalDateTime.now();
    }

    public boolean isDeleted() {
        return this.isDeleted;
    }

    /**
     * 이전 코드에서 사용하던 boardTypeId 를 위해 헬퍼 메서드를 제공한다.
     * (DTO 등에서 id 값이 필요할 때 사용)
     */
    public Long getBoardTypeId() {
        return boardType != null ? boardType.getId() : null;
    }
}
