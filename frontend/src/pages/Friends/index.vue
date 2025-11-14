<!-- src/pages/Friends/index.vue -->
<template>
  <section class="friends">
    <!-- 상단 헤더 -->
    <header class="friends__header">
      <div class="friends__header-main">
        <h1>친구&amp;그룹</h1>

        <!-- 설명 + 탭 한 줄 -->
        <div class="friends__subrow">
          <p class="friends__subtitle">
            친구와 그룹을 추가하고, 서로의 시간표와 공통 빈 시간을 확인할 수 있는 화면입니다.
          </p>

          <!-- 탭 네비게이션 -->
          <nav class="friends__tabs">
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
    <div class="friends__body">
      <!-- 친구 탭 -->
      <div v-if="activeTab === 'friends'" class="panel">
        <div class="panel__grid">
          <section class="panel__card">
            <h2 class="panel__title">친구 시간표 보기</h2>
            <p class="panel__text">
              친구를 추가해 서로의 시간표를 비교하고, 겹치는 강의나 공통 빈 시간을 확인할 수 있습니다.
            </p>
            <ul class="panel__list">
              <li>친구 검색 및 추가(초대 코드/학번/닉네임 등)</li>
              <li>친구별 시간표 공개 범위 설정(공개/부분공개/비공개)</li>
              <li>내 시간표 위에 친구 시간표 오버레이해서 한 화면에서 비교</li>
            </ul>
            <p class="panel__note">
              추후에는 실제 친구 목록과 “시간표 비교” 화면이 이 영역에 들어갈 예정입니다.
            </p>
          </section>

          <section class="panel__card panel__card--accent">
            <h2 class="panel__title">공통 빈 시간 · 겹치는 강의</h2>
            <p class="panel__text">
              선택한 친구들과의 공통 빈 시간을 자동으로 계산해 스터디/팀플 시간을 잡을 수 있습니다.
            </p>
            <ul class="panel__list">
              <li>여러 친구를 선택해 공통 빈 시간 자동 계산</li>
              <li>같은 강의를 듣는 친구 목록 확인</li>
              <li>추천 시간대를 캘린더에 일정으로 바로 추가(향후 구현)</li>
            </ul>
            <p class="panel__note">
              나중에는 공통 빈 시간에서 바로 “스터디 일정 만들기” 같은 기능을 붙일 수 있습니다.
            </p>
          </section>
        </div>
      </div>

      <!-- 그룹 탭 -->
      <div v-else-if="activeTab === 'groups'" class="panel">
        <div class="panel__grid">
          <section class="panel__card">
            <h2 class="panel__title">그룹 관리</h2>
            <p class="panel__text">
              스터디, 팀플, 동아리 등 고정 멤버가 있는 경우 그룹을 만들어 시간표와 일정을 함께 관리할 수 있습니다.
            </p>
            <ul class="panel__list">
              <li>새 그룹 생성 및 그룹 설명/태그 설정</li>
              <li>초대 코드나 링크를 통해 구성원 초대</li>
              <li>그룹별 권한(리더/멤버) 및 설정 관리</li>
            </ul>
            <p class="panel__note">
              추후 이 영역에는 실제 그룹 리스트와 그룹 설정 화면이 들어갑니다.
            </p>
          </section>

          <section class="panel__card panel__card--accent">
            <h2 class="panel__title">그룹 시간표 · 캘린더 · 공통 빈 시간</h2>
            <p class="panel__text">
              그룹 구성원 전체의 시간표를 겹쳐 보고, 모두가 가능한 공통 빈 시간을 찾아
              정기 모임이나 스터디 일정을 잡을 수 있습니다.
            </p>
            <ul class="panel__list">
              <li>그룹 전체 시간표 오버레이 보기</li>
              <li>그룹 전용 캘린더에 스터디/회의 일정 관리</li>
              <li>그룹 기준 공통 빈 시간 추천 및 일정 생성(향후 구현)</li>
            </ul>
            <p class="panel__note">
              나중에는 “그룹 공통 시간으로 일정 만들기” 같은 기능이 이쪽으로 연결될 예정입니다.
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
  { value: 'friends', label: '친구' },
  { value: 'groups', label: '그룹' },
]

const activeTab = ref('friends') // 기본은 친구 탭
</script>

<style scoped>
.friends {
  display: flex;
  flex-direction: column;
  gap: 16px;
  width: 100%;
}

/* 헤더 */
.friends__header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  width: 100%;
}

.friends__header-main {
  display: flex;
  flex-direction: column;
  gap: 6px;
  width: 100%;
}

.friends__header h1 {
  font-size: 22px;
  margin: 0;
}

/* 설명 + 탭 한 줄 */
.friends__subrow {
  display: flex;
  align-items: center;
  justify-content: space-between; /* 왼쪽 설명 / 오른쪽 탭 */
  gap: 12px;
  flex-wrap: nowrap;
  width: 100%;
}

.friends__subtitle {
  margin: 0;
  color: #666;
  font-size: 14px;
  flex: 1 1 auto; /* 남는 영역을 채워서 탭을 오른쪽으로 밀기 */
}

.friends__hint {
  margin: 0;
  font-size: 13px;
  color: #6b7280;
}

/* 탭 */
.friends__tabs {
  display: inline-flex;
  border-radius: 999px;
  padding: 3px;
  background: #f3f4f6;
  gap: 4px;
  flex-shrink: 0; /* 줄어들지 않고 오른쪽 끝 유지 */
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
.friends__body {
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
  .friends__header {
    flex-direction: column;
    align-items: flex-start;
  }

  .friends__subrow {
    flex-direction: column;
    align-items: flex-start;
  }

  .friends__tabs {
    align-self: flex-start;
  }

  .panel__grid {
    grid-template-columns: minmax(0, 1fr);
  }
}
</style>
