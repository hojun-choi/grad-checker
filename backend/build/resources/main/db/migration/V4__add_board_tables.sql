-- =======================================================
-- 1. 게시판 종류 테이블 (board_types)
-- =======================================================
CREATE TABLE board_types (
                             board_type_id BIGINT PRIMARY KEY AUTO_INCREMENT,
                             board_name VARCHAR(100) NOT NULL UNIQUE,
                             created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                             updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                             is_deleted TINYINT(1) NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- =======================================================
-- 2. 게시글 테이블 (posts)
-- =======================================================
CREATE TABLE posts (
                       post_id BIGINT PRIMARY KEY AUTO_INCREMENT,
                       user_id BIGINT NOT NULL,
                       board_type_id BIGINT NOT NULL,
                       title VARCHAR(200) NOT NULL,
                       content MEDIUMTEXT NOT NULL,
                       comment_count INT NOT NULL DEFAULT 0,
                       view_count INT NOT NULL DEFAULT 0,
                       created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                       updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                       is_deleted TINYINT(1) NOT NULL DEFAULT 0,

                       CONSTRAINT fk_posts_user FOREIGN KEY (user_id) REFERENCES users(user_id)
                           ON UPDATE CASCADE ON DELETE CASCADE,
                       CONSTRAINT fk_posts_btype FOREIGN KEY (board_type_id) REFERENCES board_types(board_type_id)
                           ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE INDEX idx_posts_btype ON posts(board_type_id);

ALTER TABLE posts ADD FULLTEXT INDEX ftx_posts (title, content);


-- =======================================================
-- 3. 댓글 테이블 (comments)
-- =======================================================
CREATE TABLE comments (
                          comment_id BIGINT PRIMARY KEY AUTO_INCREMENT,
                          post_id BIGINT NOT NULL,
                          user_id BIGINT NOT NULL,
                          parent_comment_id BIGINT NULL,
                          content TEXT NOT NULL,
                          created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                          updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                          is_deleted TINYINT(1) NOT NULL DEFAULT 0,

                          CONSTRAINT fk_comments_post FOREIGN KEY (post_id) REFERENCES posts(post_id)
                              ON UPDATE CASCADE ON DELETE CASCADE,
                          CONSTRAINT fk_comments_user FOREIGN KEY (user_id) REFERENCES users(user_id)
                              ON UPDATE CASCADE ON DELETE CASCADE,
                          CONSTRAINT fk_comments_parent FOREIGN KEY (parent_comment_id) REFERENCES comments(comment_id)
                              ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 샘플 데이터 추가
INSERT INTO board_types (board_name) VALUES ('자유게시판');
INSERT INTO board_types (board_name) VALUES ('공지사항');
INSERT INTO board_types (board_name) VALUES ('질의응답');