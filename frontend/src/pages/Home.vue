<template>
    <section>
        <h1>대시보드</h1>
        <p class="muted">아래 기능으로 이동하세요.</p>

        <div class="grid">
        <article class="card">
            <h3>졸업 요건 확인</h3>
            <p>로그인 필요. 수강 이력 업로드 후 규칙에 따라 충족 여부를 계산합니다.</p>
            <RouterLink class="btn" to="/graduate">바로가기</RouterLink>
        </article>

        <article class="card">
            <h3>게시판</h3>
            <p>열람은 누구나. 글쓰기/댓글은 로그인 후 사용 가능.</p>
            <RouterLink class="btn" to="/board">바로가기</RouterLink>
        </article>

        <article class="card">
            <h3>RAG 검색</h3>
            <p>학사/학과 공지 등에서 졸업 관련 정보를 검색(로그인 필요).</p>
            <RouterLink class="btn" to="/rag">바로가기</RouterLink>
        </article>
        </div>
    </section>
</template>

<script setup>
</script>

<style scoped>
h1{font-size:22px;margin-bottom:8px}
.muted{color:#666;margin-bottom:16px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:16px}
.card{border:1px solid #eee;border-radius:12px;padding:16px;background:#fff}
.btn{display:inline-block;margin-top:8px;border:1px solid #ddd;background:#f7f7f7;padding:6px 10px;border-radius:8px;text-decoration:none;color:#333}
</style>
