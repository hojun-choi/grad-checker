<template>
  <div v-if="open" class="overlay" @click.self="close">
    <div class="modal" role="dialog" aria-modal="true" aria-labelledby="signup-title">
      <header class="modal__head">
        <h3 id="signup-title">회원가입</h3>
        <button class="icon" @click="close" aria-label="닫기">✕</button>
      </header>

      <form class="form" @submit.prevent="onSubmit">
        <label>
          아이디
          <input v-model.trim="username" required autofocus />
        </label>
        <label>
          비밀번호
          <input v-model="password" type="password" required minlength="6" />
        </label>
        <label>
          비밀번호 확인
          <input v-model="password2" type="password" required minlength="6" />
        </label>

        <button class="btn primary" type="submit" :disabled="loading">
          {{ loading ? '가입 중…' : '가입하기' }}
        </button>
      </form>

      <p class="hint">※ 백엔드가 없으면 실패 토스트가 표시됩니다.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onBeforeUnmount } from 'vue'
import { useToast } from 'vue-toastification'
import { api } from '../../api/api.js'
import { useAuth } from '../../composables/useAuth.js'

const props = defineProps({ open: { type: Boolean, default: false } })
const emit  = defineEmits(['close','success'])

const toast = useToast()
const { login } = useAuth()

const username = ref('')
const password = ref('')
const password2 = ref('')
const loading  = ref(false)

function close(){ emit('close') }

async function onSubmit() {
  if (password.value !== password2.value) {
    toast.error('비밀번호가 일치하지 않습니다.')
    return
  }
  loading.value = true
  try {
    // 1) 회원가입
    await api.post('/auth/register', { username: username.value, password: password.value })
    // 2) 자동 로그인
    await api.post('/auth/login', { username: username.value, password: password.value })
    // 3) 현재 사용자 조회(있으면)
    try {
      const { data } = await api.get('/auth/me')
      login({ username: data?.username || username.value })
    } catch {
      login({ username: username.value })
    }
    toast.success('회원가입 및 로그인 완료!')
    emit('success'); close()
  } catch (e) {
    const status = e?.response?.status
    const msg = e?.response?.data?.message || e?.message || e
    toast.error(`회원가입 실패${status ? ' (' + status + ')' : ''}: ${msg}`)
  } finally {
    loading.value = false
  }
}

function onKeydown(e){ if (e.key === 'Escape') close() }
watch(() => props.open, v => { document.body.style.overflow = v ? 'hidden' : '' })
onMounted(() => window.addEventListener('keydown', onKeydown))
onBeforeUnmount(() => {
  window.removeEventListener('keydown', onKeydown)
  document.body.style.overflow = ''
})
</script>

<style scoped>
.overlay{position:fixed; inset:0; background:rgba(0,0,0,.35); display:flex; align-items:center; justify-content:center; z-index:1000}
.modal{width:min(420px, 92vw); background:#fff; border-radius:12px; box-shadow:0 10px 30px rgba(0,0,0,.15); padding:16px}
.modal__head{display:flex; align-items:center; justify-content:space-between; margin-bottom:8px}
.icon{border:none; background:transparent; font-size:18px; cursor:pointer}
.form{display:grid; gap:10px; margin-top:8px}
input{width:100%; padding:10px; border:1px solid #ddd; border-radius:8px}
.btn{border:1px solid #ddd; background:#f7f7f7; padding:10px 12px; border-radius:8px; cursor:pointer}
.btn.primary{background:#1f7aec; color:#fff; border-color:#1f7aec}
.hint{color:#777; font-size:12px; margin-top:8px}
</style>
