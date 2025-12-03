-- =======================================================
-- 전공/학과 테이블
-- =======================================================
CREATE TABLE IF NOT EXISTS major (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,         -- 직접 ID를 넣어도 되고, 안 넣으면 자동 증가
  name VARCHAR(100) NOT NULL UNIQUE,            -- 학과명 (중복 방지)
  is_disabled TINYINT(1) NOT NULL DEFAULT 0,    -- 0: 활성, 1: 비활성
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =======================================================
-- 사용자 테이블
-- =======================================================
CREATE TABLE IF NOT EXISTS users (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  login_id VARCHAR(50) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  username VARCHAR(50) NOT NULL,
  student_id BIGINT NOT NULL,
  major_id BIGINT NOT NULL, -- 이 컬럼이 major 테이블을 참조하게 됩니다.
  is_deleted TINYINT(1) NOT NULL DEFAULT 0,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  -- major 테이블의 id와 연결 (FK)
  CONSTRAINT fk_users_major FOREIGN KEY (major_id) 
      REFERENCES major(id) ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =======================================================
-- 게시판 종류 테이블 (board_types)
-- =======================================================
CREATE TABLE IF NOT EXISTS board_types (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  board_name VARCHAR(100) NOT NULL UNIQUE,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  is_deleted TINYINT(1) NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =======================================================
-- 게시글 테이블 (posts)
-- =======================================================
CREATE TABLE IF NOT EXISTS posts (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  user_id BIGINT NOT NULL,
  board_type_id BIGINT NOT NULL,
  title VARCHAR(200) NOT NULL,
  content MEDIUMTEXT NOT NULL,
  -- 익명 여부 (0: 실명, 1: 익명)
  is_anonymous TINYINT(1) NOT NULL DEFAULT 0,
  comment_count INT NOT NULL DEFAULT 0,
  view_count INT NOT NULL DEFAULT 0,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  is_deleted TINYINT(1) NOT NULL DEFAULT 0,

  -- users 테이블의 PK(id) 참조
  CONSTRAINT fk_posts_user FOREIGN KEY (user_id) REFERENCES users(id)
       ON UPDATE CASCADE ON DELETE CASCADE,
  -- board_types 테이블의 PK(id) 참조
  CONSTRAINT fk_posts_btype FOREIGN KEY (board_type_id) REFERENCES board_types(id)
       ON UPDATE CASCADE ON DELETE RESTRICT,

  -- 게시판별 조회를 빠르게 하기 위한 인덱스
  INDEX idx_posts_btype (board_type_id),
  -- 제목+내용 검색을 위한 풀텍스트 인덱스
  FULLTEXT INDEX ftx_posts (title, content)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =======================================================
-- 댓글 테이블 (comments)
-- =======================================================
CREATE TABLE IF NOT EXISTS comments (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  post_id BIGINT NOT NULL,
  user_id BIGINT NOT NULL,
  parent_comment_id BIGINT NULL,
  content TEXT NOT NULL,
  is_anonymous TINYINT(1) NOT NULL DEFAULT 0,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  is_deleted TINYINT(1) NOT NULL DEFAULT 0,

  -- posts 테이블의 id 참조
  CONSTRAINT fk_comments_post FOREIGN KEY (post_id) REFERENCES posts(id)
      ON UPDATE CASCADE ON DELETE CASCADE,
  -- users 테이블의 id 참조
  CONSTRAINT fk_comments_user FOREIGN KEY (user_id) REFERENCES users(id)
      ON UPDATE CASCADE ON DELETE CASCADE,
  -- 자기 자신의 id 참조 (대댓글용)
  CONSTRAINT fk_comments_parent FOREIGN KEY (parent_comment_id) REFERENCES comments(id)
      ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =======================================================
-- RAG 질의응답 로그 (질문과 답변만 저장)
-- =======================================================
CREATE TABLE IF NOT EXISTS rag_logs (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  user_id BIGINT NULL,            -- 질문한 유저 (로그인 안 했으면 NULL)
  question TEXT NOT NULL,         -- 사용자의 질문 (query)
  answer MEDIUMTEXT NOT NULL,     -- AI의 답변 (answer)
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

  -- user_id가 users 테이블의 id를 참조 (유저 삭제 시 로그의 작성자는 NULL 처리)
  CONSTRAINT fk_rag_logs_user FOREIGN KEY (user_id) REFERENCES users(id)
      ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =======================================================
-- RAG 참조 문서 메타데이터 및 점수 (본문 제외)
-- =======================================================
CREATE TABLE IF NOT EXISTS rag_references (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  rag_log_id BIGINT NOT NULL,     -- 어떤 질문(rag_logs)에 대한 참조인지 연결

  -- 1) 메타데이터 (metadata)
  title VARCHAR(255) NOT NULL,    -- metadata.title
  department VARCHAR(100) NULL,   -- metadata.department
  link VARCHAR(1000) NOT NULL,    -- metadata.link
  published_date DATE NULL,       -- metadata.date (YYYY-MM-DD)

  -- 2) 검색 점수 데이터 (docs 바로 아래)
  rrf_score DOUBLE NULL,          -- docs.rrf_score
  combined_score DOUBLE NULL,     -- docs.combined_score
  recency_score DOUBLE NULL,      -- docs.recency_score

  -- rag_logs가 삭제되면 이 참조 정보들도 같이 삭제됨
  CONSTRAINT fk_rag_ref_log FOREIGN KEY (rag_log_id) REFERENCES rag_logs(id)
      ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =======================================================
-- 연도별 전공/학과 히스토리 (major_history)
-- =======================================================
CREATE TABLE IF NOT EXISTS major_history (
  id BIGINT PRIMARY KEY AUTO_INCREMENT, -- 자동 증가 PK
  current_major_id BIGINT NOT NULL,     -- major 테이블의 id (FK)
  year INT NOT NULL,                    -- 연도 (2020, 2021...)
  college VARCHAR(100) NOT NULL,        -- 단과대
  faculty VARCHAR(100) NOT NULL,        -- 학부
  tt_major VARCHAR(100) NOT NULL,       -- 시간표용 약어
  major_name VARCHAR(100) NOT NULL,     -- 전공명 (당시 기준 이름)
  category VARCHAR(50) NOT NULL,        -- 전공 구분
  
  is_deleted TINYINT(1) NOT NULL DEFAULT 0, -- 0: 활성, 1: 비활성 (폐지된 학과 등)
  
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  -- major 테이블의 id와 연결 (Foreign Key)
  -- major 테이블의 id가 변경되면 여기도 같이 변경(CASCADE)
  -- major 테이블의 데이터가 삭제되려 할 때 이 히스토리가 있으면 삭제 막음(RESTRICT)
  CONSTRAINT fk_history_major FOREIGN KEY (current_major_id) 
      REFERENCES major(id) ON UPDATE CASCADE ON DELETE RESTRICT,

  -- 같은 학과는 같은 연도에 중복 등록 불가!
  CONSTRAINT uk_major_history_year UNIQUE (current_major_id, year),

  -- 검색 성능을 위한 인덱스
  INDEX idx_major_history_year (year),
  INDEX idx_major_history_name (major_name),
  INDEX idx_major_history_cur_id (current_major_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =======================================================
-- 강의 시간표 메인 테이블 (lecture_timetable)
-- =======================================================
CREATE TABLE IF NOT EXISTS lecture_timetable (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,

  -- 학년도 및 학기 (termCode "20-2" 분리)
  year INT NOT NULL,              -- 예: 2020
  semester VARCHAR(20) NOT NULL,  -- 예: "2학기"

  -- 강의 기본 정보
  course_code VARCHAR(30) NOT NULL,   -- courseCode (분반별로 코드가 다르므로 유니크 식별 가능)
  course_title VARCHAR(200) NOT NULL, -- courseTitle
  section_no VARCHAR(10) NULL,        -- sectionNo
  instructor_name VARCHAR(100) NULL,  -- instructorName
  department_name VARCHAR(100) NULL,  -- departmentName (개설 학과)
  
  -- 학점 및 시간 정보
  course_credits DOUBLE NOT NULL DEFAULT 0.0, -- credit.courseCredits
  lecture_hours DOUBLE NOT NULL DEFAULT 0.0,  -- credit.lectureHours
  design_credits DOUBLE NOT NULL DEFAULT 0.0, -- credit.designCredits

  -- 수강 인원 및 상태
  capacity INT NOT NULL DEFAULT 0,
  enrolled_count INT NOT NULL DEFAULT 0,
  
  -- 기타 정보
  class_type_info VARCHAR(50) NULL,            -- classTypeInfo(강좌유형정보)
  taking_note TEXT NULL,                       -- takingNote(수강유의사항)
  target_students VARCHAR(200) NULL,           -- targetStudents(수강대상)
  engineering_certification VARCHAR(100) NULL, -- engineeringCertification(공학인증)

  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  -- 학교 특성상 과목코드(분반 포함)가 유니크하므로 유니크 키 설정
  CONSTRAINT uk_lecture_timetable UNIQUE (year, semester, course_code),

  -- 검색 성능을 위한 인덱스
  INDEX idx_lecture_year_sem (year, semester),
  INDEX idx_lecture_title (course_title)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =======================================================
-- 강의 시간/장소 테이블 (lecture_schedule)
-- =======================================================
-- 강의 하나에 여러 수업 시간(월 13:30, 수 15:00 등)이 있을 수 있으므로 분리
CREATE TABLE IF NOT EXISTS lecture_schedule (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  
  lecture_id BIGINT NOT NULL,       -- lecture_timetable의 id (FK)
  
  meeting_day VARCHAR(10) NOT NULL, -- meetingDay (예: "월")
  start_time TIME NOT NULL,         -- startTime (예: "13:30:00")
  end_time TIME NOT NULL,           -- endTime (예: "14:45:00")
  building_room VARCHAR(100) NULL,  -- buildingRoom

  -- 부모 강의 삭제 시 시간표도 자동 삭제
  CONSTRAINT fk_schedule_lecture FOREIGN KEY (lecture_id) 
      REFERENCES lecture_timetable(id) ON UPDATE CASCADE ON DELETE CASCADE,

  -- 같은 강의가 같은 요일/시간에 중복 등록되는 것을 방지
  CONSTRAINT uk_lecture_schedule UNIQUE (lecture_id, meeting_day, start_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =======================================================
-- 강의 이수 구분/인정 학과 테이블 (lecture_eligibility)
-- =======================================================
-- 강의 하나가 여러 학과(소프트-전기, 컴퓨터-복선)에서 인정될 수 있으므로 분리
CREATE TABLE IF NOT EXISTS lecture_eligibility (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  
  lecture_id BIGINT NOT NULL,            -- lecture_timetable의 id (FK)
  
  department_name VARCHAR(100) NOT NULL, -- 인정 학과 (예: 소프트, 컴퓨터)
  category_type VARCHAR(50) NOT NULL,    -- 이수 구분 (예: 전기, 전선, 복선)

  -- 부모 강의 삭제 시 인정 정보도 자동 삭제
  CONSTRAINT fk_eligibility_lecture FOREIGN KEY (lecture_id) 
      REFERENCES lecture_timetable(id) ON UPDATE CASCADE ON DELETE CASCADE,

  -- 중복 방지
  CONSTRAINT uk_lecture_eligibility UNIQUE (lecture_id, department_name, category_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
