<template>
  <section class="editor">
    <header class="editor__header">
      <div>
        <h1>{{ pageTitle }}</h1>
        <p class="editor__subtitle">
          졸업 요건, 시간표, 전과/복수전공, 수업 정보 등 학교 생활과 관련된 내용을 자유롭게 작성해주세요.
        </p>
      </div>
    </header>

    <form class="editor__form" @submit.prevent="handleSubmit">
      <div class="editor__row">
        <div class="field field--inline field--board">
          <label class="label">게시판명</label>
          <select v-model="form.category" class="control" required>
            <option disabled value="">게시판명을 선택해주세요</option>
            <option
              v-for="cat in categoryOptions"
              :key="cat.value"
              :value="cat.value"
            >
              {{ cat.label }}
            </option>
          </select>
        </div>

        <div class="field field--inline field--title">
          <div class="field__title-head">
            <label class="label">제목</label>
            <p class="hint">{{ form.title.length }}/100</p>
          </div>
          <input
            v-model="form.title"
            type="text"
            class="control"
            maxlength="100"
            placeholder="제목을 입력해주세요 (100자 이내)"
            required
          />
        </div>

        <div class="field field--inline field--author">
          <label class="label">작성자 표시</label>
          <label class="checkbox">
            <input
              type="checkbox"
              v-model="isAnonymous"
            />
            <span>익명으로 표시</span>
          </label>
          <p class="hint">체크하면 게시글 작성자가 '익명'으로 표시됩니다.</p>
        </div>
      </div>

      <div class="field">
        <label class="label">내용</label>
        <textarea
          v-model="form.content"
          class="control control--textarea"
          rows="12"
          placeholder="졸업 요건, 시간표, 전과 경험, 수업 후기 등 구체적으로 적어주시면 더 도움이 됩니다."
          required
        ></textarea>
      </div>

      <div class="editor__actions">
        <button type="button" class="btn btn--ghost" @click="handleCancel">
          취소
        </button>

        <div class="editor__actions-right">
          <button type="submit" class="btn btn--primary" :disabled="isLoading">
            {{ submitLabel }}
          </button>
        </div>
      </div>
    </form>
  </section>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuth } from '../../composables/useAuth.js'
import { api } from '../../api/api.js'
import { useToast } from 'vue-toastification' // Toast import

const route = useRoute()
const router = useRouter()
const { isAuthenticated } = useAuth()
const toast = useToast() // Toast instance

const isAuthed = computed(() => isAuthenticated())
const isEditMode = computed(() => !!route.params.id) // /board/:id/edit

// 상태 관리
const isLoading = ref(false)
const categoryOptions = ref([]) // 서버에서 받아올 게시판 목록

const form = ref({
  category: '', // PostRequest.boardName 대응
  title: '',
  content: '',
})

// 익명 여부 (PostRequest.anonymous 대응)
const isAnonymous = ref(true)

const pageTitle = computed(() =>
  isEditMode.value ? '게시글 수정' : '새 글 쓰기'
)

const submitLabel = computed(() => {
  if (isLoading.value) return '처리 중...'
  return isEditMode.value ? '수정 완료' : '등록하기'
})

// 게시판 목록 불러오기
const fetchBoardTypes = async () => {
  try {
    const res = await api.get('/board/posts', {
      params: { page: 0, size: 0 }
    })
    if (res.data?.boardTypes) {
      categoryOptions.value = res.data.boardTypes.map(bt => ({
        label: bt.boardName,
        value: bt.boardName
      }))
    }
  } catch (error) {
    console.error('게시판 종류 불러오기 실패:', error)
    toast.error('게시판 정보를 불러오는데 실패했습니다.')
  }
}

// 수정 시 기존 글 정보 불러오기
const fetchPostDetail = async (id) => {
  try {
    const res = await api.get(`/board/posts/${id}`)
    const data = res.data
    form.value.category = data.category
    form.value.title = data.title
    form.value.content = data.content
    isAnonymous.value = data.anonymous
  } catch (error) {
    console.error('게시글 정보 불러오기 실패:', error)
    toast.error('게시글 정보를 불러오지 못했습니다.')
    router.push('/board')
  }
}

onMounted(async () => {
  if (!isAuthed.value) {
    toast.warning('로그인 후 글쓰기를 이용할 수 있습니다.')
    router.push('/board')
    return
  }

  // 게시판 종류 조회
  await fetchBoardTypes()

  // 수정 모드라면 상세 내용 조회
  if (isEditMode.value) {
    await fetchPostDetail(route.params.id)
  }
})

async function handleSubmit() {
  // 유효성 검사 - Warning Toast
  if (!form.value.category) {
    toast.warning('게시판명을 선택해주세요.')
    return
  }
  if (!form.value.title.trim()) {
    toast.warning('제목을 입력해주세요.')
    return
  }
  if (!form.value.content.trim()) {
    toast.warning('내용을 입력해주세요.')
    return
  }

  const payload = {
    boardName: form.value.category,
    title: form.value.title.trim(),
    content: form.value.content.trim(),
    anonymous: isAnonymous.value,
  }

  try {
    isLoading.value = true
    if (isEditMode.value) {
      // 수정
      const id = route.params.id
      await api.put(`/board/posts/${id}`, payload)
      toast.success('게시글이 수정되었습니다.')
    } else {
      // 등록
      await api.post('/board/posts', payload)
      toast.success('게시글이 등록되었습니다.')
    }
    // 목록으로 이동
    router.push('/board')
  } catch (error) {
    console.error('글 저장 실패:', error)
    toast.error('글 저장 중 오류가 발생했습니다.')
  } finally {
    isLoading.value = false
  }
}

function handleCancel() {
  if (confirm('작성 중인 내용이 사라집니다. 목록으로 돌아갈까요?')) {
    router.back()
  }
}
</script>

<style scoped>
.editor {
  display: flex;
  flex-direction: column;
  gap: 16px;
  width: 100%;
}

/* 본문 전체 폭 사용 */
.editor__form {
  width: 100%;
  max-width: 100%;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.editor__header {
  width: 100%;
  max-width: 100%;
  margin: 0 0 8px;
}

.editor__header h1 {
  font-size: 22px;
  margin: 0 0 4px;
}

.editor__subtitle {
  margin: 0;
  color: #666;
  font-size: 14px;
}

/* 첫 줄 (게시판명 / 제목 / 작성자 표시) */
.editor__row {
  display: flex;
  gap: 12px;
  width: 100%;
}

/* 필드 공통 */
.field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.field--inline {
  flex: 1;
}

.field--board {
  max-width: 220px;
}

.field--title {
  flex: 2;
}

.field--author {
  max-width: 150px;
}

.field__title-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.label {
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.control {
  border-radius: 8px;
  border: 1px solid #ddd;
  padding: 8px 10px;
  font-size: 14px;
  outline: none;
  width: 100%;
  box-sizing: border-box;
  background-color: #fff;
}

.control:focus {
  border-color: #1f7aec;
  box-shadow: 0 0 0 1px rgba(31, 122, 236, 0.15);
}

.control--textarea {
  resize: vertical;
  min-height: 240px;
}

/* 힌트 */
.hint {
  margin: 0;
  font-size: 12px;
  color: #999;
  text-align: right;
}

/* 작성자 표시 체크박스 */
.checkbox {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #444;
  height: 38px; /* input height와 유사하게 */
  padding-left: 4px;
}

.checkbox input[type='checkbox'] {
  margin: 0;
  width: 16px;
  height: 16px;
  accent-color: #1f7aec;
  cursor: pointer;
}

/* 하단 버튼들 */
.editor__actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 8px;
  gap: 8px;
}

.editor__actions-right {
  display: flex;
  gap: 8px;
}

/* 버튼 */
.btn {
  border: 1px solid #ddd;
  background: #f7f7f7;
  padding: 8px 14px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.btn:hover {
  filter: brightness(0.95);
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn--primary {
  background: #1f7aec;
  border-color: #1f7aec;
  color: #fff;
}

.btn--ghost {
  background: #fff;
  color: #444;
}

/* 모바일 대응 */
@media (max-width: 800px) {
  .editor__row {
    flex-direction: column;
  }

  .field--board,
  .field--author {
    max-width: 100%;
  }
  
  .checkbox {
    height: auto;
    padding: 8px 0;
  }
}

@media (max-width: 640px) {
  .editor__actions {
    flex-direction: column-reverse;
    align-items: stretch;
  }

  .editor__actions-right {
    width: 100%;
    justify-content: flex-end;
  }
  
  .editor__actions-right .btn {
    width: 100%;
  }

  .btn {
    width: 100%;
    text-align: center;
  }
}
</style>