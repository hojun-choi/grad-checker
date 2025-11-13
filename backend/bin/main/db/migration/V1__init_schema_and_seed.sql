CREATE TABLE student (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  student_no VARCHAR(32) NOT NULL UNIQUE,
  name VARCHAR(64) NOT NULL,
  catalog_year INT NOT NULL
);

CREATE TABLE course (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  code VARCHAR(32) NOT NULL UNIQUE,
  name VARCHAR(128) NOT NULL,
  credits INT NOT NULL,
  type VARCHAR(16) NOT NULL,
  ge_area VARCHAR(32) NULL
);

CREATE TABLE taken_course (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  student_id BIGINT NOT NULL,
  course_code VARCHAR(32) NOT NULL,
  grade VARCHAR(4) NOT NULL,
  term VARCHAR(16) NOT NULL,
  UNIQUE(student_id, course_code, term),
  FOREIGN KEY (student_id) REFERENCES student(id)
);

CREATE TABLE requirement_group (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  code VARCHAR(32) NOT NULL,
  name VARCHAR(128) NOT NULL
);

CREATE TABLE requirement_rule (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  catalog_year INT NOT NULL,
  group_code VARCHAR(32) NOT NULL,
  rule_type VARCHAR(32) NOT NULL,
  params_json TEXT NOT NULL
);

INSERT INTO student (student_no, name, catalog_year) VALUES
('20230001', '홍길동', 2023);

INSERT INTO course (code, name, credits, type, ge_area) VALUES
('CS101', '프로그래밍입문', 3, 'MAJOR', NULL),
('CS201', '자료구조', 3, 'MAJOR', NULL),
('CS301', '데이터베이스', 3, 'MAJOR', NULL),
('GE101', '대학글쓰기', 3, 'GE', 'BASIC'),
('GE102', '기초수학', 3, 'GE', 'BASIC'),
('GE201', '인문핵심', 3, 'GE', 'CORE'),
('GE202', '사회핵심', 3, 'GE', 'CORE'),
('FREE001', '자유선택세미나', 2, 'FREE', NULL);

INSERT INTO requirement_rule (catalog_year, group_code, rule_type, params_json)
VALUES (2023, 'TOTAL', 'CREDITS_AT_LEAST', '{"credits":130}');

INSERT INTO requirement_rule (catalog_year, group_code, rule_type, params_json)
VALUES (2023, 'MAJOR', 'CREDITS_AT_LEAST', '{"credits":60}');

INSERT INTO requirement_rule (catalog_year, group_code, rule_type, params_json)
VALUES (2023, 'GE', 'CREDITS_AT_LEAST', '{"credits":30}');

INSERT INTO requirement_rule (catalog_year, group_code, rule_type, params_json)
VALUES
(2023, 'GE', 'GE_AREA_AT_LEAST', '{"area":"BASIC","credits":12}'),
(2023, 'GE', 'GE_AREA_AT_LEAST', '{"area":"CORE","credits":12}'),
(2023, 'GE', 'GE_AREA_AT_LEAST', '{"area":"BALANCE","credits":6}');

INSERT INTO requirement_rule (catalog_year, group_code, rule_type, params_json)
VALUES
(2023, 'MAJOR_REQ', 'INCLUDE_COURSES', '{"codes":["CS201","CS301"]}');

