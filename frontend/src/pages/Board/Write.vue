<!-- src/pages/Board/Write.vue -->
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
      <!-- 첫 줄: 게시판명 / 제목 / 작성자 표시 -->
      <div class="editor__row">
        <!-- 게시판명 -->
        <div class="field field--inline field--board">
          <label class="label">게시판명</label>
          <select v-model="form.category" class="control">
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

        <!-- 제목 -->
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
          />
        </div>

        <!-- 작성자 표시 -->
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

      <!-- 내용 -->
      <div class="field">
        <label class="label">내용</label>
        <textarea
          v-model="form.content"
          class="control control--textarea"
          rows="12"
          placeholder="졸업 요건, 시간표, 전과 경험, 수업 후기 등 구체적으로 적어주시면 더 도움이 됩니다."
        ></textarea>
      </div>

      <!-- 하단 버튼 -->
      <div class="editor__actions">
        <button type="button" class="btn btn--ghost" @click="handleCancel">
          취소
        </button>

        <div class="editor__actions-right">
          <button type="submit" class="btn btn--primary">
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

const route = useRoute()
const router = useRouter()
const { isAuthenticated } = useAuth()

const isAuthed = computed(() => isAuthenticated())
const isEditMode = computed(() => !!route.params.id) // /board/:id/edit 에서 재사용

const categoryOptions = [
  { value: 'grad',   label: '졸업 요건' },
  { value: 'course', label: '수강 / 시간표' },
  { value: 'major',  label: '전과 / 복수전공' },
  { value: 'free',   label: '자유글' },
]

const form = ref({
  category: '',
  title: '',
  content: '',
})

// 익명 여부
const isAnonymous = ref(true)

const pageTitle = computed(() =>
  isEditMode.value ? '게시글 수정' : '새 글 쓰기'
)

const submitLabel = computed(() =>
  isEditMode.value ? '수정 완료' : '등록하기'
)

onMounted(() => {
  if (!isAuthed.value) {
    alert('로그인 후 글쓰기를 이용할 수 있습니다.')
    router.push('/board')
    return
  }

  if (isEditMode.value) {
    const id = route.params.id
    // TODO: 여기서 GET /api/board/:id 호출해서 form/isAnonymous 채우기
    form.value = {
      category: 'grad',
      title: `예시 제목 (글 ID: ${id})`,
      content: 'TODO: 서버에서 게시글 내용을 불러와서 채워 넣으세요.',
    }
    // 예시: 서버에서 anonymous 값 받아왔다고 가정
    isAnonymous.value = true
  }
})

function handleSubmit() {
  if (!form.value.category) {
    alert('게시판명을 선택해주세요.')
    return
  }
  if (!form.value.title.trim()) {
    alert('제목을 입력해주세요.')
    return
  }
  if (!form.value.content.trim()) {
    alert('내용을 입력해주세요.')
    return
  }

  const payload = {
    category: form.value.category,
    title: form.value.title.trim(),
    content: form.value.content.trim(),
    anonymous: isAnonymous.value, // 백엔드에서 true면 '익명'으로 처리
  }

  if (isEditMode.value) {
    const id = route.params.id
    // TODO: PUT /api/board/{id}
    console.log('EDIT POST', id, payload)
    alert('수정된 걸로 가정하고 목록으로 이동합니다.')
  } else {
    // TODO: POST /api/board
    console.log('CREATE POST', payload)
    alert('등록된 걸로 가정하고 목록으로 이동합니다.')
  }

  router.push('/board')
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
  max-width: 260px;
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

.label__sub {
  margin-left: 4px;
  font-weight: 400;
  font-size: 12px;
  color: #888;
}

.control {
  border-radius: 8px;
  border: 1px solid #ddd;
  padding: 8px 10px;
  font-size: 14px;
  outline: none;
  width: 100%;
  box-sizing: border-box;
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
}

.checkbox input[type='checkbox'] {
  margin: 0;
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

  .btn {
    width: 100%;
    text-align: center;
  }
}
</style>
