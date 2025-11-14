<template>
  <header class="nav">
    <div class="left">
      <RouterLink to="/" class="brand">Graduation Checker</RouterLink>
      <nav class="links">
        <RouterLink to="/">대시보드</RouterLink>
        <RouterLink to="/board">게시판</RouterLink>
        <RouterLink to="/schedule">시간표·졸업 관리</RouterLink>
        <RouterLink to="/friends">친구&amp;그룹</RouterLink>
        <RouterLink to="/rag">공지 검색AI</RouterLink>
      </nav>
    </div>

    <div class="right">
      <template v-if="isAuthed">
        <span class="hello">안녕하세요, {{ displayName }}님</span>
        <button class="btn" @click="onLogout">로그아웃</button>
      </template>
      <template v-else>
        <button class="btn" @click="openLogin = true">로그인</button>
        <button class="btn primary" @click="openSignup = true">회원가입</button>
      </template>
    </div>

    <!-- moved: pages/Auth/*.vue -->
    <LoginModal :open="openLogin" @close="openLogin=false" @success="onLoggedIn" />
    <SignUpModal :open="openSignup" @close="openSignup=false" @success="onSignedUp" />
  </header>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'vue-toastification'
import { useAuth } from '../composables/useAuth.js'

// ⬇️ 경로 변경
import LoginModal from '../pages/Auth/LoginModal.vue'
import SignUpModal from '../pages/Auth/SignUpModal.vue'

const router = useRouter()
const toast = useToast()

const openLogin  = ref(false)
const openSignup = ref(false)

const { user, logout } = useAuth()
const isAuthed    = computed(() => !!user.value)
const displayName = computed(() => user.value?.username ?? '')

function onLoggedIn(){ /* 추가 액션 필요 시 */ }
function onSignedUp(){ toast.success('환영합니다!') }
function onLogout(){
  logout()
  toast.info('로그아웃되었습니다.')
  router.push({ name: 'home' })
}
</script>

<style scoped>
.nav{display:flex;align-items:center;justify-content:space-between;padding:12px 16px;border-bottom:1px solid #eee;background:#fff;position:sticky;top:0;z-index:10}
.brand{font-weight:700;color:#222;text-decoration:none;margin-right:12px}
.links a{margin-right:20px;color:#333;text-decoration:none}
.links a.router-link-active{font-weight:600}
.btn{border:1px solid #ddd;background:#f7f7f7;padding:6px 10px;border-radius:8px;cursor:pointer}
.btn.primary{background:#1f7aec;color:#fff;border-color:#1f7aec;margin-left:8px}
.hello{margin-right:8px;color:#555}
</style>
