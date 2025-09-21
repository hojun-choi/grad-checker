# Grad Checker – Dockerized Spring Boot + MySQL + Frontend

> 졸업요건 사정표(데이터베이스응용 1조) 프로젝트를 **도커 한 번**으로 올리고, 수정할 때 뭘 바꿔야 하는지까지 정리한 사용설명서입니다. 도커 처음 써도 그대로 따라 하면 됩니다.

---

## 1) 프로젝트 개요

* **Backend**: Spring Boot 3.5.x (Java 17), JPA(Hibernate), Flyway(마이그레이션), MySQL Connector
* **DB**: MySQL 8.0
* **Frontend**: 정적 빌드 + Nginx (프런트에서 `/api`로 호출하면 Nginx가 백엔드(8080)으로 프록시)
* **Container Orchestration**: Docker Compose

### 주요 엔드포인트

* 데이터 업로드: `POST /api/import/taken`

  * Body(JSON 배열): `[{"studentNo":"20230001","courseCode":"CS201","grade":"A","term":"2024-1"}]`
* 평가 조회(예시): `GET /api/evaluate?studentNo=20230001`
* 프런트 URL: `http://localhost:8081`

---

## 2) 디렉터리 구조

```
grad-checker/
├─ backend/                       # Spring Boot 소스
│  ├─ build.gradle.kts            # 백엔드 의존성/플러그인 정의
│  ├─ src/main/resources/
│  │  ├─ application.yml          # Spring 설정(데이터소스/JPA/Flyway 등)
│  │  └─ db/migration/            # Flyway SQL 마이그레이션(V1__*.sql ...)
│  └─ Dockerfile                  # 백엔드 이미지 빌드 규칙
├─ frontend/                      # 프런트엔드(정적 빌드 결과를 Nginx로 서비스)
│  └─ Dockerfile                  # 프런트엔드 이미지 빌드 규칙
├─ docker-compose.yml             # 전체 서비스(db/backend/frontend) 정의
├─ .env                           # 포트/DB 접속 등 환경변수
└─ README.md                      # 이 파일
```

---

## 3) 실행 전 요구사항

* Windows / macOS / Linux
* **Docker Desktop** 설치 (Compose 포함)
* 로컬에서 **3306** 포트를 이미 쓰는 MySQL이 있다면 꺼두거나, 이 프로젝트는 기본적으로 **호스트 3307 → 컨테이너 3306**으로 매핑합니다(.env에서 `MYSQL_PORT=3307`).

---

## 4) 환경변수(.env)

아래 값이 기본으로 설정되어 있습니다. 필요 시 수정하세요.

```
DB_HOST=db
DB_PORT=3306
DB_NAME=grad
DB_USER=app
DB_PASSWORD=app1234

BACKEND_PORT=8080
FRONTEND_PORT=8081
MYSQL_PORT=3307
```

* **중요**: 컨테이너끼리 통신할 때는 호스트 포트가 아니라 **서비스명과 컨테이너 포트**를 사용합니다.

  * 백엔드 → DB 연결 URL은 `jdbc:mysql://db:3306/grad` 형태(Compose 네트워크).
  * 호스트에서 DB 접속 시에는 `localhost:3307` 사용(호스트 포트 매핑).

---

## 5) 첫 실행(빌드 → 기동 → 확인)

### 5.1 이미지 빌드

```bash
# 전체 이미지(백엔드/프런트) 빌드
docker compose build --no-cache
```

### 5.2 컨테이너 실행

```bash
# 백그라운드 실행
docker compose up -d
```

### 5.3 상태 확인

```bash
# 컨테이너 리스트
docker compose ps

# 개별 로그 보기(백엔드)
docker compose logs backend --tail=150 -f

# 개별 로그 보기(DB)
docker compose logs db --tail=80 -f
```

* 백엔드 로그에 `Tomcat initialized with port 8080` 와 Flyway `Schema up to date` 비슷한 메시지가 보이면 정상.

### 5.4 동작 테스트

* **프런트**: 브라우저에서 `http://localhost:8081`
* **백엔드 헬스(404면 정상 구동)**:

  * Windows CMD

    ```cmd
    curl -s -o NUL -w "HTTP %%{http_code}\n" http://localhost:8080/
    ```
  * PowerShell은 `curl`이 `Invoke-WebRequest` 별칭이라 옵션이 달라집니다. 간단히:

    ```powershell
    Invoke-WebRequest http://localhost:8080/ -UseBasicParsing | Select-Object StatusCode
    ```
* **데이터 업로드 테스트(CMD)**

  ```cmd
  curl -X POST http://localhost:8080/api/import/taken -H "Content-Type: application/json" -d "[{\"studentNo\":\"20230001\",\"courseCode\":\"CS201\",\"grade\":\"A\",\"term\":\"2024-1\"}]"
  ```

  * 성공 시: `{"status":"ok","inserted":1}`

---

## 6) 개발/수정 시 워크플로

### 6.1 백엔드 의존성 추가/수정

1. `backend/build.gradle.kts` 에 의존성 추가

```kotlin
dependencies {
    implementation("그룹:이름:버전")
    // 예) implementation("org.springframework.boot:spring-boot-starter-cache")
}
```

2. 이미지 재빌드 & 재기동

```bash
# 백엔드만 다시 빌드
docker compose build backend
# 변경사항 반영하여 재시작
docker compose up -d backend
```

> 모든 서비스를 새로 빌드하고 싶으면 `docker compose up -d --build` 사용.

### 6.2 프런트엔드 수정

* 정적 프런트 코드를 수정했다면

```bash
# 프런트만 빌드 & 재기동
docker compose build frontend && docker compose up -d frontend
```

### 6.3 DB 스키마 변경(Flyway)

* **절대 수동으로 테이블을 직접 바꾸지 마세요.**
* 새 SQL을 `backend/src/main/resources/db/migration/` 에 추가합니다.

  * 파일명 예: `V2__add_something.sql`
* 컨테이너 재시작 시 Flyway가 자동 적용합니다.
* JPA 엔티티 타입 변경 시 **DDL과 엔티티 타입이 일치**해야 합니다. (예: `tinytext` vs `text` 타입 이슈 등)

### 6.4 설정 변경

* 포트/DB 비밀번호 등은 \*\*`.env`\*\*에서 바꿉니다.
* DB 접속 URL을 강제로 지정해야 할 때는 `docker-compose.yml`의 `backend.environment`에 있는 아래 세 개를 사용합니다.

  * `SPRING_DATASOURCE_URL`
  * `SPRING_DATASOURCE_USERNAME`
  * `SPRING_DATASOURCE_PASSWORD`

---

## 7) 자주 쓰는 도커 명령어(설명 포함)

```bash
# 컨테이너 시작/중지/삭제
docker compose up -d           # 백그라운드로 시작
docker compose down            # 중지 + 네트워크 해제
docker compose down -v         # + 볼륨 삭제(DB 초기화)

# 로그 확인
docker compose logs backend -f # 백엔드 로그 팔로우
docker compose logs db -f      # DB 로그 팔로우

# 특정 컨테이너 재빌드/재기동
docker compose build backend   # 백엔드 이미지 재빌드
docker compose up -d backend   # 백엔드만 재시작

# 컨테이너 내부로 진입(쉘)
docker compose exec backend sh

# DB 접속(MySQL 클라이언트)
docker compose exec db sh -lc "mysql -uapp -papp1234 grad"

# 네트워크에서 서비스명 해석 확인 + 포트 체크
docker compose run --rm --entrypoint sh backend -lc "apk add --no-cache busybox-extras >/dev/null 2>&1 || true; getent hosts db; nc -zv db 3306"
```

> **설명**
>
> * `up -d`: detached(백그라운드) 실행
> * `down -v`: 컨테이너/네트워크/볼륨 모두 제거(로컬 DB 데이터 초기화)
> * `build`: Dockerfile 기준으로 이미지 생성
> * `exec`: 실행 중인 컨테이너 내부에서 명령 실행
> * `run --rm`: 일회성 컨테이너 실행 후 바로 삭제

---

## 8) 트러블슈팅

### 8.1 포트 충돌(3306/8080/8081)

* 에러: `listen tcp 0.0.0.0:3306: bind: Only one usage of each socket address ...`
* 원인: 호스트 3306에 다른 MySQL이 떠 있음.
* 해결: `.env`의 `MYSQL_PORT`를 3307로 유지(기본값)하거나, 로컬 MySQL 서비스를 종료.

### 8.2 백엔드가 DB에 연결 못함(Communications link failure)

* 체크리스트:

  * `docker compose ps`에서 `db`가 **healthy**인지 확인.
  * 백엔드 환경변수: `SPRING_DATASOURCE_URL=jdbc:mysql://db:3306/grad`
  * Compose가 `depends_on: service_healthy`로 설정되어 있어야 함(이미 설정됨).

### 8.3 Flyway 버전/DB 버전 호환

* 과거 에러: `Unsupported Database: MySQL 8.x`
* 조치: **Flyway 9.22.3**으로 고정. (build.gradle.kts 참고)

### 8.4 스키마 검증 오류(DDL 불일치)

* 예: `Schema-validation: wrong column type ... params_json ... found [text], expecting [tinytext]`
* 해결:

  * 엔티티의 `@Column(columnDefinition = "tinytext")`처럼 DDL을 명시적으로 맞추거나
  * Flyway 마이그레이션에서 컬럼 타입을 수정(`ALTER TABLE ... MODIFY COLUMN ...`).

---

## 9) 백엔드/프런트 도커파일 개요

### 9.1 backend/Dockerfile (멀티 스테이지)

* 1단계: Gradle 이미지로 `bootJar` 빌드 → `app.jar` 생성
* 2단계: Java 17 JRE 이미지로 경량 런타임 구성(`/app/app.jar` 실행)

### 9.2 frontend/Dockerfile

* Node로 빌드 → Nginx에 `/usr/share/nginx/html`로 복사
* `location /api/ { proxy_pass http://backend:8080/; }` 로 백엔드 프록시

---

## 10) 업데이트 가이드(요약)

* **의존성 추가**: `backend/build.gradle.kts` → `docker compose build backend` → `docker compose up -d backend`
* **엔드포인트 추가**: Spring Controller/Service/Repository 코드 추가 → 위와 동일하게 재빌드/재기동
* **DB 구조 변경**: `db/migration`에 `V{번호}__{설명}.sql` 추가 → 백엔드 재시작 시 자동 반영
* **프런트 수정**: 소스 수정 → `docker compose build frontend` → `docker compose up -d frontend`
* **포트 변경**: `.env` 수정(예: `FRONTEND_PORT=8082`) → `docker compose up -d`

---

## 11) 유용한 확인 명령(Windows)

```cmd
:: 백엔드 루트 응답 코드(404면 서버 살아 있음)
curl -s -o NUL -w "HTTP %%{http_code}\n" http://localhost:%BACKEND_PORT%/

:: 업로드 API 테스트
curl -X POST http://localhost:%BACKEND_PORT%/api/import/taken -H "Content-Type: application/json" -d "[{\"studentNo\":\"20230001\",\"courseCode\":\"CS201\",\"grade\":\"A\",\"term\":\"2024-1\"}]"
```

---

## 12) 문의/추가 변경 시

* 새 이슈가 생기면 **오류 로그**(`docker compose logs backend --tail=200`)를 먼저 첨부해 주세요.
* DB/엔티티 타입 오류는 대개 **Flyway 마이그레이션 또는 엔티티 DDL 설정**과 연관되어 있습니다.

행복한 디버깅 되세요! 🚀
