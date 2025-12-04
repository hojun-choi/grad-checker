<template>
  <section class="planner">
    <header class="planner__header">
      <div class="planner__header-main">
        <h1>시간표·졸업 관리</h1>
        <div class="planner__subrow">
          <p class="planner__subtitle">
            내 시간표와 캘린더를 관리하고, 졸업 요건 충족 여부를 한눈에 확인하는 공간
          </p>

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

    <div class="planner__body">
      <TimetableTab v-if="activeTab === 'timetable'" />
      <GraduationTab v-else-if="activeTab === 'graduation'" />
    </div>
  </section>
</template>

<script setup>
import { ref } from 'vue'
import TimetableTab from './components/TimetableTab.vue'
import GraduationTab from './components/GraduationTab.vue'

/* 탭 설정 */
const tabs = [
  { value: 'timetable', label: '내 시간표' },
  { value: 'graduation', label: '졸업 요건' },
]
const activeTab = ref('timetable')
</script>

<style scoped>
/* 전체 레이아웃 잡는 CSS만 남김 */
.planner {
  display: flex;
  flex-direction: column;
  gap: 16px;
  width: 100%;
}

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

.planner__subrow {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: nowrap;
  width: 100%;
}

.planner__subtitle {
  margin: 0;
  color: #666;
  font-size: 14px;
  flex: 1 1 auto;
}

.planner__tabs {
  display: inline-flex;
  border-radius: 999px;
  padding: 3px;
  background: #f3f4f6;
  gap: 4px;
  flex-shrink: 0;
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

.planner__body {
  border-radius: 12px;
  border: 1px solid #eee;
  background: #fff;
  padding: 18px 20px;
  min-height: 600px;
}

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
}
</style>