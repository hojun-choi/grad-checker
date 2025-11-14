<!-- src/pages/Schedule/index.vue -->
<template>
  <section class="planner">
    <!-- 상단 헤더 -->
    <header class="planner__header">
      <div class="planner__header-main">
        <h1>시간표·졸업 관리</h1>

        <!-- 설명 + 탭을 한 줄에 배치 -->
        <div class="planner__subrow">
          <p class="planner__subtitle">
            내 시간표와 캘린더를 관리하고, 졸업 요건 충족 여부를 한 곳에서 확인할 수 있는 화면입니다.
          </p>

          <!-- 탭 네비게이션 -->
          <nav class="planner__tabs">
            <button
              v-for="tab in tabs"
              :key="tab.value"
              type="button"
              class="tab"
              :class="{ 'tab--active': activeTab === tab.value }"
              @click="activeTab = tab.value"
            >
              {{ tab.label }}
            </button>
          </nav>
        </div>
      </div>
    </header>

    <!-- 탭별 본문 -->
    <div class="planner__body">
      <!-- 내 시간표 탭 -->
      <div v-if="activeTab === 'timetable'" class="panel">
        <section class="panel__card">
          <h2 class="panel__title">내 시간표 관리</h2>
          <p class="panel__text">
            여러 개의 시간표를 생성·저장해두고, 학기별로 관리하는 공간입니다.
            가장 최근에 사용한 시간표를 기본으로 보여주도록 구현할 예정입니다.
          </p>
          <ul class="panel__list">
            <li>여러 버전의 시간표 생성 · 수정 · 삭제</li>
            <li>학교 시간표(강의명/교수/교시)와 연동</li>
            <li>졸업 요건과 연계된 시간표 추천(향후 구현)</li>
          </ul>
          <p class="panel__note">
            추후 여기에는 실제 주간 시간표 그리드 컴포넌트가 들어가게 됩니다.
          </p>
        </section>
      </div>

      <!-- 내 캘린더 탭 -->
      <div v-else-if="activeTab === 'calendar'" class="panel">
        <section class="panel__card">
          <h2 class="panel__title">내 캘린더</h2>
          <p class="panel__text">
            강의 일정뿐 아니라 과제 마감, 시험, 스터디 등 개인 일정을 함께 관리하는 캘린더입니다.
          </p>
          <ul class="panel__list">
            <li>주/월 단위 일정 보기</li>
            <li>강의 시간 자동 반영</li>
            <li>과제·시험 일정 추가 및 알림(향후 구현)</li>
          </ul>
          <p class="panel__note">
            추후에는 친구·그룹 기능과 연계해, 공통 일정이나 스터디 일정을 캘린더에 바로 추가할 수 있도록 확장할 수 있습니다.
          </p>
        </section>
      </div>

      <!-- 졸업 요건 탭 -->
      <div v-else-if="activeTab === 'graduation'" class="panel">
        <div class="panel__grid">
          <section class="panel__card">
            <h2 class="panel__title">졸업 요건 요약</h2>
            <p class="panel__text">
              여기에서 전체 이수 학점, 전공/교양, 균형교양, 전필·필수 과목 등
              졸업에 필요한 요건을 한눈에 볼 수 있습니다.
            </p>
            <ul class="panel__list">
              <li>총 이수 학점 / 필요한 학점</li>
              <li>전공 필수·선택 / 교양 학점</li>
              <li>캡스톤·졸업 프로젝트 이수 여부</li>
            </ul>
            <p class="panel__note">
              추후에 실제 수강 이력 업로드 후, 자동으로 충족 여부를 계산하는 영역이 들어갈 자리입니다.
            </p>
          </section>

          <section class="panel__card panel__card--accent">
            <h2 class="panel__title">이번 학기 계획과 연계</h2>
            <p class="panel__text">
              시간표·캘린더에서 설정한 이번 학기 수강 계획을 바탕으로,
              졸업 요건에 얼마나 가까워졌는지 체크할 수 있습니다.
            </p>
            <p class="panel__text">
              나중에는 “이번 학기 추가로 들어야 할 추천 과목” 같은 기능도 이쪽에 녹일 수 있습니다.
            </p>
          </section>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useAuth } from '../../composables/useAuth.js'

const { isAuthenticated } = useAuth()
const isAuthed = computed(() => isAuthenticated())

const tabs = [
  { value: 'timetable', label: '내 시간표' },
  { value: 'calendar', label: '내 캘린더' },
  { value: 'graduation', label: '졸업 요건' },
]

const activeTab = ref('timetable') // 기본은 내 시간표 탭
</script>

<style scoped>
.planner {
  display: flex;
  flex-direction: column;
  gap: 16px;
  width: 100%;
}

/* 헤더 */
.planner__header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  width: 100%;
}

.planner__header-main {
  display: flex;
  flex-direction: column;
  gap: 6px;
  width: 100%;
}

.planner__header h1 {
  font-size: 22px;
  margin: 0;
}

/* 설명 + 탭 한 줄 */
.planner__subrow {
  display: flex;
  align-items: center;
  justify-content: space-between; /* 왼쪽 설명 / 오른쪽 탭 */
  gap: 12px;
  flex-wrap: nowrap;
  width: 100%;
}

.planner__subtitle {
  margin: 0;
  color: #666;
  font-size: 14px;
  flex: 1 1 auto; /* 남는 영역을 채우게 해서 탭을 오른쪽 끝으로 밀어냄 */
}

.planner__hint {
  margin: 0;
  font-size: 13px;
  color: #6b7280;
}

/* 탭 */
.planner__tabs {
  display: inline-flex;
  border-radius: 999px;
  padding: 3px;
  background: #f3f4f6;
  gap: 4px;
  flex-shrink: 0; /* 줄어들지 않고 오른쪽에 딱 붙게 */
}

.tab {
  border: none;
  background: transparent;
  padding: 6px 14px;
  border-radius: 999px;
  font-size: 13px;
  cursor: pointer;
  color: #6b7280;
}

.tab--active {
  background: #1f7aec;
  color: #fff;
  box-shadow: 0 2px 4px rgba(37, 99, 235, 0.3);
}

/* 본문 */
.planner__body {
  border-radius: 12px;
  border: 1px solid #eee;
  background: #fff;
  padding: 18px 20px;
}

.panel {
  width: 100%;
}

.panel__grid {
  display: grid;
  grid-template-columns: minmax(0, 1.2fr) minmax(0, 1fr);
  gap: 16px;
}

.panel__card {
  border-radius: 10px;
  border: 1px solid #eef0f4;
  padding: 14px 16px;
  background: #fafbff;
}

.panel__card--accent {
  background: #f5f3ff;
  border-color: #e0e7ff;
}

.panel__title {
  margin: 0 0 8px;
  font-size: 16px;
  font-weight: 600;
}

.panel__text {
  margin: 0 0 8px;
  font-size: 14px;
  color: #4b5563;
  line-height: 1.6;
}

.panel__list {
  margin: 0 0 8px;
  padding-left: 18px;
  font-size: 13px;
  color: #4b5563;
}

.panel__list li + li {
  margin-top: 2px;
}

.panel__note {
  margin: 0;
  font-size: 12px;
  color: #9ca3af;
}

/* 모바일 대응 */
@media (max-width: 768px) {
  .planner__header {
    flex-direction: column;
    align-items: flex-start;
  }

  .planner__subrow {
    flex-direction: column;
    align-items: flex-start;
  }

  .planner__tabs {
    align-self: flex-start;
  }

  .panel__grid {
    grid-template-columns: minmax(0, 1fr);
  }
}
</style>
