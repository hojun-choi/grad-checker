<template>
  <section>
    <h1>대시보드</h1>
    <p class="muted">아래 기능으로 바로 이동할 수 있습니다.</p>

    <div class="grid">
      <article class="card">
        <h3>게시판</h3>
        <p>졸업 요건, 시간표, 전과/복수전공 등 정보를 서로 공유하는 공간입니다.<br>열람은 누구나, 글쓰기/댓글은 로그인 후 이용 가능합니다.</p>
        <RouterLink class="btn" to="/board">바로가기</RouterLink>
      </article>

      <article class="card">
        <h3>시간표·졸업 관리</h3>
        <p>내 시간표와 캘린더를 관리하고, 졸업 요건 충족 여부를 한눈에 확인할 수 있습니다.<br>로그인 후 이용 가능합니다.</p>
        <RouterLink class="btn" to="/schedule">바로가기</RouterLink>
      </article>

      <article class="card">
        <h3>친구&amp;그룹</h3>
        <p>친구와 그룹을 추가해서 서로의 시간표를 비교하고, 공통 빈 시간이나 겹치는 강의를 확인할 수 있습니다.<br>로그인 후 이용 가능합니다.</p>
        <RouterLink class="btn" to="/friends">바로가기</RouterLink>
      </article>

      <article class="card">
        <h3>공지 검색AI</h3>
        <p>학교·학과 공지, 규정 등을 기반으로 궁금한 내용을 검색할 수 있는 기능입니다.<br>로그인 후 이용 가능합니다.</p>
        <RouterLink class="btn" to="/rag">바로가기</RouterLink>
      </article>
    </div>
  </section>
</template>

<script setup>
</script>

<style scoped>
h1 {
  font-size: 22px;
  margin-bottom: 8px;
}
.muted {
  color: #666;
  margin-bottom: 16px;
}
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 16px;
}
.card {
  border: 1px solid #eee;
  border-radius: 12px;
  padding: 16px;
  background: #fff;
}
.btn {
  display: inline-block;
  margin-top: 8px;
  border: 1px solid #ddd;
  background: #f7f7f7;
  padding: 6px 10px;
  border-radius: 8px;
  text-decoration: none;
  color: #333;
}
</style>
