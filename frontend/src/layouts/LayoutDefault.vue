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
  max-width: 1080px;
  margin: 24px auto;
  padding: 0 16px;
}

/* (선택) 헤더/푸터가 절대 커지지 않도록 명시 */
:deep(header), :deep(footer) {
  flex: 0 0 auto;
}
</style>
