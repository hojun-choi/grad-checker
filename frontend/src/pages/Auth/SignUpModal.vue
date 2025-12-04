<template>
  <div v-if="open" class="overlay" @click.self="close">
    <div class="modal" role="dialog" aria-modal="true" aria-labelledby="signup-title">
      <header class="modal__head">
        <h3 id="signup-title">회원가입</h3>
        <button class="icon" @click="close" aria-label="닫기">✕</button>
      </header>

      <form class="form" @submit.prevent="onSubmit">
        <!-- 아이디 + 중복확인 -->
        <label class="field-row">
          <span>아이디</span>
          <div class="field-row__inner">
            <input
              v-model.trim="loginId"
              required
              autocomplete="off"
              placeholder="로그인에 사용할 아이디"
            />
            <button
              type="button"
              class="btn secondary small"
              @click="checkLoginId"
              :disabled="checkingId || !loginId"
            >
              {{ checkingId ? '확인 중…' : '중복확인' }}
            </button>
          </div>
          <p class="field-hint" v-if="idChecked">
            <span v-if="idAvailable" class="ok">사용 가능한 아이디입니다.</span>
            <span v-else class="err">이미 사용 중인 아이디입니다.</span>
          </p>
        </label>

        <!-- 비밀번호 -->
        <label>
          비밀번호
          <input
            v-model="password"
            type="password"
            required
            minlength="6"
            placeholder="6자 이상 입력"
          />
        </label>

        <!-- 비밀번호 확인 -->
        <label>
          비밀번호 확인
          <input
            v-model="password2"
            type="password"
            required
            minlength="6"
          />
        </label>

        <!-- 닉네임 (username) -->
        <label>
          닉네임
          <input
            v-model.trim="name"
            required
            placeholder="사용할 이름"
          />
        </label>

        <!-- 학번: 숫자만 -->
        <label>
          학번
          <input
            v-model.number="studentId"
            type="number"
            required
            inputmode="numeric"
            min="0"
            step="1"
            placeholder="예: 20221234"
          />
        </label>

        <!-- 전공 선택: 3단 셀렉트 (college → faculty → major_name) -->
        <label>
          단과대 선택
          <select
            v-model="selectedCollege"
            :disabled="loadingMajors || !collegeOptions.length"
          >
            <option value="" disabled>단과대를 선택해 주세요</option>
            <option
              v-for="c in collegeOptions"
              :key="c"
              :value="c"
            >
              {{ c }}
            </option>
          </select>
          <p class="field-hint">
            2025학년도 기준 <code>학부전공</code> 단과대 목록입니다.
          </p>
        </label>

        <label>
          학부/학과 선택
          <select
            v-model="selectedFaculty"
            :disabled="!selectedCollege || !facultyOptions.length"
          >
            <option value="" disabled>학부/학과를 선택해 주세요</option>
            <option
              v-for="f in facultyOptions"
              :key="f"
              :value="f"
            >
              {{ f }}
            </option>
          </select>
          <p class="field-hint">
            먼저 단과대를 선택하면 해당 단과대의 학부/학과 목록이 표시됩니다.
          </p>
        </label>

        <label>
          전공 선택
          <select
            v-model="selectedMajorName"
            :disabled="!selectedFaculty || !majorNameOptions.length"
          >
            <option value="" disabled>전공을 선택해 주세요</option>
            <option
              v-for="m in majorNameOptions"
              :key="m"
              :value="m"
            >
              {{ m }}
            </option>
          </select>
          <p class="field-hint">
            전공까지 선택하면 해당 전공의 <code>current_major_id</code>가 회원 전공으로 저장됩니다.
          </p>
        </label>

        <button
          class="btn primary"
          type="submit"
          :disabled="loading || !canSubmit"
        >
          {{ loading ? '가입 중…' : '가입하기' }}
        </button>
      </form>

      <p class="hint">
        ※ 아이디 중복확인과 전공 선택까지 완료해야 가입할 수 있습니다.
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onBeforeUnmount, computed } from 'vue'
import { useToast } from 'vue-toastification'
import { api } from '../../api/api.js'
import { useAuth } from '../../composables/useAuth.js'

const props = defineProps({ open: { type: Boolean, default: false } })
const emit  = defineEmits(['close','success'])

const toast = useToast()
const { login } = useAuth()

// 전공 필터 고정값 (major_history.year, category)
const FIXED_MAJOR_YEAR = 2025
const FIXED_MAJOR_CATEGORY = '학부전공'

// 폼 필드
const loginId  = ref('')
const password = ref('')
const password2 = ref('')
const name = ref('')
// 숫자 형태로 관리
const studentId = ref(null)

// major_history rows
// [{id, currentMajorId, college, faculty, ttMajor, majorName, category}, ...] 기대
const majors = ref([])

// 3단 셀렉트 상태
const selectedCollege = ref('')
const selectedFaculty = ref('')
const selectedMajorName = ref('')

// 상태 플래그
const loading = ref(false)
const loadingMajors = ref(false)

const checkingId = ref(false)
const idChecked = ref(false)
const idAvailable = ref(false)

// 아이디가 바뀌면 중복확인 상태 초기화
watch(loginId, () => {
  idChecked.value = false
  idAvailable.value = false
})

// 단과대가 바뀌면 밑 단계 리셋
watch(selectedCollege, () => {
  selectedFaculty.value = ''
  selectedMajorName.value = ''
})

// 학부가 바뀌면 전공 리셋
watch(selectedFaculty, () => {
  selectedMajorName.value = ''
})

// 모달 열릴 때 폼 초기화 + 전공 목록 로딩
watch(
  () => props.open,
  async (v) => {
    document.body.style.overflow = v ? 'hidden' : ''
    if (v) {
      resetForm()
      await loadMajors()
    }
  }
)

function resetForm() {
  loginId.value = ''
  password.value = ''
  password2.value = ''
  name.value = ''
  studentId.value = null
  majors.value = []

  selectedCollege.value = ''
  selectedFaculty.value = ''
  selectedMajorName.value = ''

  loading.value = false
  loadingMajors.value = false
  checkingId.value = false
  idChecked.value = false
  idAvailable.value = false
}

// =========================
// 전공 목록 관련 computed
// =========================

// 단과대 리스트 (중복 제거)
const collegeOptions = computed(() => {
  const set = new Set()
  for (const m of majors.value) {
    if (m.college) set.add(m.college)
  }
  return Array.from(set)
})

// 선택된 단과대 기준 학부/학과 리스트 (중복 제거)
const facultyOptions = computed(() => {
  if (!selectedCollege.value) return []
  const set = new Set()
  for (const m of majors.value) {
    if (m.college === selectedCollege.value && m.faculty) {
      set.add(m.faculty)
    }
  }
  return Array.from(set)
})

// 선택된 단과대 + 학부 기준 전공명 리스트 (중복 제거)
const majorNameOptions = computed(() => {
  if (!selectedCollege.value || !selectedFaculty.value) return []
  const set = new Set()
  for (const m of majors.value) {
    if (m.college === selectedCollege.value &&
        m.faculty === selectedFaculty.value &&
        m.majorName) {
      set.add(m.majorName)
    }
  }
  return Array.from(set)
})

// 최종 선택된 전공의 current_major_id
const finalMajorCurrentId = computed(() => {
  if (!selectedCollege.value || !selectedFaculty.value || !selectedMajorName.value) {
    return null
  }
  const row = majors.value.find(
    (m) =>
      m.college === selectedCollege.value &&
      m.faculty === selectedFaculty.value &&
      m.majorName === selectedMajorName.value
  )
  return row ? row.currentMajorId : null
})

// 아이디 중복확인
async function checkLoginId() {
  if (!loginId.value.trim()) {
    toast.error('아이디를 입력해 주세요.')
    return
  }
  checkingId.value = true
  try {
    // 백엔드: GET /auth/check-login-id?loginId=...
    const { data } = await api.get('/auth/check-login-id', {
      params: { loginId: loginId.value.trim() },
    })

    const available = !!data?.available
    idChecked.value = true
    idAvailable.value = available

    if (available) {
      toast.success('사용 가능한 아이디입니다.')
    } else {
      toast.error('이미 사용 중인 아이디입니다.')
    }
  } catch (e) {
    idChecked.value = false
    idAvailable.value = false
    const msg = e?.response?.data?.message || e?.message || e
    toast.error(`아이디 중복확인 실패: ${msg}`)
  } finally {
    checkingId.value = false
  }
}

// 전공 목록 불러오기 (year=2025, category=학부전공)
async function loadMajors() {
  loadingMajors.value = true
  majors.value = []

  try {
    // 백엔드: GET /majors/history?year=2025&category=학부전공
    const { data } = await api.get('/majors/history', {
      params: {
        year: FIXED_MAJOR_YEAR,
        category: FIXED_MAJOR_CATEGORY,
      },
    })

    majors.value = Array.isArray(data) ? data : []

    if (!majors.value.length) {
      toast.warning('전공 목록이 비어 있습니다. (year=2025, category=학부전공)')
    }
  } catch (e) {
    const msg = e?.response?.data?.message || e?.message || e
    toast.error(`전공 목록을 불러오지 못했습니다: ${msg}`)
  } finally {
    loadingMajors.value = false
  }
}

const canSubmit = computed(() => {
  return (
    !!loginId.value &&
    !!password.value &&
    !!password2.value &&
    !!name.value &&
    studentId.value !== null &&
    Number.isInteger(studentId.value) &&
    studentId.value > 0 &&
    !!finalMajorCurrentId.value &&      // 전공까지 선택 완료
    idChecked.value &&
    idAvailable.value &&
    password.value.length >= 6 &&
    password2.value.length >= 6
  )
})

function close() {
  emit('close')
}

// 실제 회원가입
async function onSubmit() {
  if (!canSubmit.value) {
    toast.error('입력값을 다시 확인해 주세요.')
    return
  }

  if (password.value !== password2.value) {
    toast.error('비밀번호가 일치하지 않습니다.')
    return
  }

  if (!idChecked.value || !idAvailable.value) {
    toast.error('아이디 중복확인을 먼저 해 주세요.')
    return
  }

  if (!finalMajorCurrentId.value) {
    toast.error('전공을 선택해 주세요.')
    return
  }

  if (studentId.value === null || !Number.isInteger(studentId.value) || studentId.value <= 0) {
    toast.error('학번을 올바른 숫자로 입력해 주세요.')
    return
  }

  loading.value = true
  try {
    const payload = {
      loginId: loginId.value.trim(),
      password: password.value,
      username: name.value.trim(),
      // 숫자로 전송
      studentId: studentId.value,
      // finalMajorCurrentId → users.major_id
      majorId: Number(finalMajorCurrentId.value),
    }

    // 1) 회원가입
    await api.post('/auth/register', payload)

    // 2) 자동 로그인 (loginId 기준)
    await api.post('/auth/login', {
      username: loginId.value.trim(),
      password: password.value,
    })

    // 3) /auth/me 로 유저 정보 조회 후 전역 상태에 반영
    try {
      const { data } = await api.get('/auth/me')
      login({
        username: data?.username || name.value.trim(),
        loginId: data?.loginId || loginId.value.trim(),
      })
    } catch {
      login({
        username: name.value.trim(),
        loginId: loginId.value.trim(),
      })
    }

    toast.success('회원가입 및 로그인 완료!')
    emit('success')
    close()
  } catch (e) {
    const status = e?.response?.status
    const msg = e?.response?.data?.message || e?.message || e
    toast.error(`회원가입 실패${status ? ' (' + status + ')' : ''}: ${msg}`)
  } finally {
    loading.value = false
  }
}

function onKeydown(e) {
  if (e.key === 'Escape') close()
}

onMounted(() => window.addEventListener('keydown', onKeydown))
onBeforeUnmount(() => {
  window.removeEventListener('keydown', onKeydown)
  document.body.style.overflow = ''
})
</script>

<style scoped>
.overlay{position:fixed; inset:0; background:rgba(0,0,0,.35); display:flex; align-items:center; justify-content:center; z-index:1000}
.modal{width: min(460px, 92vw); background:#fff; border-radius:12px; box-shadow:0 10px 30px rgba(0,0,0,.15); padding:16px}
.modal__head{display:flex; align-items:center; justify-content:space-between; margin-bottom:8px}
.icon{border:none; background:transparent; font-size:18px; cursor:pointer}
.form{display:grid; gap:10px; margin-top:8px}
input, select{width:100%; padding:10px; border:1px solid #ddd; border-radius:8px}
.btn{border:1px solid #ddd; background:#f7f7f7; padding:10px 12px; border-radius:8px; cursor:pointer}
.btn.primary{background:#1f7aec; color:#fff; border-color:#1f7aec}
.btn.secondary{background:#f3f4f6; color:#111827; border-color:#d1d5db}
.btn.small{padding:6px 10px; font-size:0.8rem}
.btn:disabled{opacity:.6; cursor:default}
.hint{color:#777; font-size:12px; margin-top:8px}

/* 아이디 + 버튼 같은 라인 */
.field-row{display:flex; flex-direction:column; gap:4px}
.field-row__inner{display:flex; gap:6px; align-items:center}
.field-row__inner input{flex:1}
.field-hint{margin:0; font-size:11px; color:#6b7280}
.field-hint .ok{color:#16a34a}
.field-hint .err{color:#b91c1c}
code{background:#f3f4f6; padding:1px 4px; border-radius:4px; font-size:11px}
</style>
