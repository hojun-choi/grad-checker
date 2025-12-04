<template>
  <section class="dashboard">
    <header class="dashboard__header">
      <div>
        <h1>대시보드</h1>
        <p class="dashboard__subtitle">
          학업 관리의 모든 것. 주요기능과 AI 공지 검색를 한 곳에서
        </p>
      </div>
    </header>

    <div class="dashboard__layout">
      <section class="dashboard__cards">
        <article class="dashboard__card">
          <h2>게시판</h2>
          <p>
            졸업 요건, 시간표, 전과/복수전공 등 정보를 서로 공유하는 공간
          </p>
          <RouterLink to="/board" class="dashboard__card-button">입장하기</RouterLink>
        </article>

        <article class="dashboard__card">
          <h2>시간표·졸업 관리</h2>
          <p>
            내 시간표와 캘린더를 관리하고, 졸업 요건 충족 여부를 한눈에 확인하는 공간
          </p>
          <RouterLink to="/schedule" class="dashboard__card-button">관리하기</RouterLink>
        </article>

        <article class="dashboard__card">
          <h2>친구&그룹</h2>
          <p>
            친구와 그룹을 추가해서 서로의 시간표를 비교하고, 공통 빈 시간이나 강좌를 확인하는 공간
          </p>
          <RouterLink to="/friends" class="dashboard__card-button">바로가기</RouterLink>
        </article>
      </section>

      <section class="dashboard__rag">
        <RagPage />
      </section>
    </div>
  </section>
</template>

<script setup>
import { RouterLink } from 'vue-router'
import RagPage from '../Rag/index.vue'
</script>

<style scoped>
.dashboard {
  display: flex;
  flex-direction: column;
  gap: 16px;
  width: 100%;
}

/* 헤더 */
.dashboard__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  width: 100%;
}

.dashboard__header h1 {
  font-size: 22px;
  margin: 0;
}

.dashboard__subtitle {
  margin: 0;
  font-size: 14px;
  color: #666;
}

/* 2열 레이아웃 */
.dashboard__layout {
  display: flex;
  align-items: flex-start;
  gap: 24px;
}

/* 왼쪽 카드 컬럼 */
.dashboard__cards {
  flex: 0 0 260px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* 카드 스타일 수정됨: Flex Column 적용 */
.dashboard__card {
  background: #ffffff;
  border-radius: 12px;
  border: 1px solid #eee;
  padding: 14px 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);

  /* [핵심 수정] 내부 요소를 세로로 배치 */
  display: flex;
  flex-direction: column;
}

.dashboard__card h2 {
  margin: 0 0 6px;
  font-size: 0.95rem;
  font-weight: 600;
}

.dashboard__card p {
  margin: 0 0 10px;
  font-size: 0.85rem;
  color: #4b5563;
  line-height: 1.4;
  
  /* 내용이 짧아도 버튼을 아래로 밀어내려면 아래 주석 해제 */
  /* flex-grow: 1; */
}

/* 버튼 스타일 수정됨: 오른쪽 정렬 추가 */
.dashboard__card-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 6px 12px;
  border-radius: 999px;
  border: 1px solid #d1d5db;
  font-size: 0.8rem;
  text-decoration: none;
  color: #111827;
  background: #f9fafb;
  transition: background 0.15s ease, border-color 0.15s ease;

  /* [핵심 수정] 버튼을 오른쪽 끝으로 보냄 */
  align-self: flex-end;
  /* 버튼 위쪽에 여백 확보 (선택사항) */
  margin-top: auto; 
}

.dashboard__card-button:hover {
  background: #e5edff;
  border-color: #c7d2fe;
}

/* 오른쪽 RAG 영역 */
.dashboard__rag {
  flex: 1;
  min-width: 0;
}

/* 반응형 */
@media (max-width: 900px) {
  .dashboard__layout {
    flex-direction: column;
  }

  .dashboard__cards {
    flex: 1 1 auto;
    flex-direction: row;
    flex-wrap: wrap;
    gap: 12px;
  }

  .dashboard__card {
    flex: 1 1 220px;
  }
}
</style>