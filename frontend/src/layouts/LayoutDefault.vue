<template>
  <div class="layout">
    <NavBar />
    <main class="content">
      <slot />
    </main>
    <AppFooter />
  </div>
</template>

<script setup>
import NavBar from '../components/NavBar.vue'
import AppFooter from '../components/AppFooter.vue'
</script>

<style scoped>
/* 레이아웃 전체를 세로 플렉스, 화면 높이 최소 100vh */
.layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* 본문만 남은 공간 전부 차지 */
.content {
  flex: 1 0 auto;
  width: 100%;        /* 전체 폭 사용 */
  max-width: none;    /* 1080px 제한 제거 */
  margin: 24px 0 32px; /* 위/아래만 여백 */
  padding: 0 32px;    /* 좌우 여백만 살짝 */
  box-sizing: border-box;
}

/* (선택) 헤더/푸터가 절대 커지지 않도록 명시 */
:deep(header), :deep(footer) {
  flex: 0 0 auto;
}
</style>
