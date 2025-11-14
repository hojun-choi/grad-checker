<template>
    <footer class="foot">
        <div class="links">
            <a href="https://ssu.ac.kr" target="_blank" rel="noreferrer">학교 홈페이지</a>
            <a href="https://saint.ssu.ac.kr" target="_blank" rel="noreferrer">유세인트</a>
            <a href="https://ssu.factchat.bot/auth" target="_blank" rel="noreferrer">팩트챗(숭실대 LLM)</a>
            <a href="https://canvas.ssu.ac.kr/" target="_blank" rel="noreferrer">숭실대 LMS</a>
            <a href="https://library.ssu.ac.kr" target="_blank" rel="noreferrer">학교 도서관</a>
            <a href="https://path.ssu.ac.kr/" target="_blank" rel="noreferrer">슈패스(SSU-PATH)</a>
        </div>
        <small>© {{ new Date().getFullYear() }} Graduation Checker</small>
    </footer>
</template>

<script setup>
</script>

<style scoped>
.foot{margin-top:32px;padding:16px;border-top:1px solid #eee;color:#666}
.links{display:flex;gap:20px;margin-bottom:6px;flex-wrap:wrap}
.links a{color:#444;text-decoration:none}
.links a:hover{text-decoration:underline}
</style>
