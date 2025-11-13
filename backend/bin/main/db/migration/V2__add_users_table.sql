-- V2__add_users_table.sql

-- 1) 계정 테이블 (student_id FK 추가)
CREATE TABLE IF NOT EXISTS `users` (
  `user_id` BIGINT PRIMARY KEY AUTO_INCREMENT,
  `login_id` VARCHAR(50) NOT NULL UNIQUE,
  `password_hash` VARCHAR(255) NOT NULL,
  `username` VARCHAR(50) NOT NULL,
  `email` VARCHAR(120) NOT NULL,

  -- student 테이블과 연결 (1:1)
  `student_id` BIGINT NULL UNIQUE,

  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `is_deleted` TINYINT(1) NOT NULL DEFAULT 0,

  CONSTRAINT `fk_users_student` FOREIGN KEY (`student_id`)
    REFERENCES `student`(`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE INDEX idx_users_email ON users(email);

