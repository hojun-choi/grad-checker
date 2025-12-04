<template>
  <div class="panel">
    <div class="panel__grid">
      <section class="panel__card">
        <h2 class="panel__title">졸업 요건 요약</h2>
        <p class="panel__text">
          여기에서 전체 이수 학점, 전공/교양, 균형교양, 전필·필수 과목 등 졸업에
          필요한 요건을 한눈에 볼 수 있습니다.
        </p>
        <ul class="panel__list">
          <li>총 이수 학점 / 필요한 학점</li>
          <li>전공 필수·선택 / 교양 학점</li>
        </ul>
      </section>

      <section class="panel__card panel__card--accent">
        <h2 class="panel__title">이번 학기 계획과 연계</h2>
        <p class="panel__text">
          시간표·캘린더에서 설정한 이번 학기 수강 계획을 바탕으로, 졸업 요건에
          얼마나 가까워졌는지 체크할 수 있습니다.
        </p>
      </section>
    </div>
  </div>
</template>

<script setup>
// 추후 졸업 요건 로직 추가
</script>

<style scoped>
.panel { width: 100%; }
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
.panel__title { margin: 0 0 8px; font-size: 16px; font-weight: 600; }
.panel__text { margin: 0 0 8px; font-size: 14px; color: #4b5563; line-height: 1.6; }
.panel__list { margin: 0 0 8px; padding-left: 18px; font-size: 13px; color: #4b5563; }
.panel__list li + li { margin-top: 2px; }

@media (max-width: 768px) {
  .panel__grid { grid-template-columns: minmax(0, 1fr); }
}
</style>