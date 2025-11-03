<!-- src/pages/Auth/LoginModal.vue -->
<template>
  <div v-if="open" class="overlay" @click.self="close">
    <div class="modal" role="dialog" aria-modal="true" aria-labelledby="login-title">
      <header class="modal__head">
        <h3 id="login-title">로그인</h3>
        <button class="icon" @click="close" aria-label="닫기">✕</button>
      </header>

      <form class="form" @submit.prevent="onSubmit">
        <label>
          아이디
          <input v-model="username" required autofocus />
        </label>
        <label>
          비밀번호
          <input v-model="password" type="password" required />
        </label>

        <button class="btn primary" type="submit" :disabled="loading">
          {{ loading ? '로그인 중…' : '로그인' }}
        </button>
      </form>

      <p class="hint">
        ※ 데모: 백엔드가 없으면 실패로 떨어져 토스트가 표시됩니다.
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onBeforeUnmount } from 'vue'
import { useToast } from 'vue-toastification'
import { useAuth } from '../../composables/useAuth.js'
import { api } from '../../api/api.js'

const props = defineProps({ open: { type: Boolean, default: false } })
const emit  = defineEmits(['close','success'])

const toast = useToast()
const { login } = useAuth()

const username = ref('')
const password = ref('')
const loading  = ref(false)

function close() { emit('close') }

async function onSubmit() {
  loading.value = true
  try {
    // 1) 로그인 요청 (세션/쿠키 부여 기대)
    await api.post('/auth/login', {
      username: username.value,
      password: password.value,
    })

    // 2) 현재 사용자 조회로 화면 상태 동기화 (선택이지만 권장)
    //    서버가 { username, roles: [...] } 형태로 준다고 가정
    try {
      const { data } = await api.get('/auth/me')
      // useAuth의 간단 상태와도 일단 호환되게 username만 넣어 둠
      login({ username: data?.username || username.value })
    } catch {
      // /auth/me가 아직 없거나 실패해도 UX는 진행
      login({ username: username.value })
    }

    toast.success('로그인되었습니다.')
    emit('success')
    close()
  } catch (e) {
    // 상태 코드/메시지 최대한 보여주기
    const status = e?.response?.status
    const msg = e?.response?.data?.message || e?.message || e
    toast.error(`로그인 실패${status ? ' (' + status + ')' : ''}: ${msg}`)
  } finally {
    loading.value = false
  }
}

// ESC로 닫기 + 스크롤 잠금
function onKeydown(e){ if (e.key === 'Escape') close() }
watch(() => props.open, (v) => { document.body.style.overflow = v ? 'hidden' : '' })
onMounted(() => window.addEventListener('keydown', onKeydown))
onBeforeUnmount(() => {
  window.removeEventListener('keydown', onKeydown)
  document.body.style.overflow = ''
})
</script>

<style scoped>
.overlay{
  position:fixed; inset:0; background:rgba(0,0,0,.35);
  display:flex; align-items:center; justify-content:center; z-index:1000;
}
.modal{
  width:min(420px, 92vw); background:#fff; border-radius:12px;
  box-shadow:0 10px 30px rgba(0,0,0,.15); padding:16px;
}
.modal__head{display:flex; align-items:center; justify-content:space-between; margin-bottom:8px}
.icon{border:none; background:transparent; font-size:18px; cursor:pointer}
.form{display:grid; gap:10px; margin-top:8px}
input{width:100%; padding:10px; border:1px solid #ddd; border-radius:8px}
.btn{border:1px solid #ddd; background:#f7f7f7; padding:10px 12px; border-radius:8px; cursor:pointer}
.btn.primary{background:#1f7aec; color:#fff; border-color:#1f7aec}
.hint{color:#777; font-size:12px; margin-top:8px}
</style>
