<!-- src/pages/Board/Detail.vue -->
<template>
  <section class="post">
    <!-- 로딩 / 에러 -->
    <div v-if="loading" class="post__state">불러오는 중...</div>
    <div v-else-if="error" class="post__state post__state--error">
      {{ error }}
      <button class="btn" type="button" @click="goList">목록으로</button>
    </div>

    <!-- 본문 -->
    <div v-else class="post__card">
      <!-- 상단: 제목 / 메타 / 버튼 -->
      <header class="post__header">
        <div class="post__header-main">
          <h1 class="post__title">{{ post.title }}</h1>

          <div class="post__meta">
            <span class="badge" :data-cat="post.category">
              {{ categoryLabel(post.category) }}
            </span>

            <span class="post__meta-dot">·</span>
            <span class="post__meta-item">작성자 {{ post.author }}</span>

            <span class="post__meta-dot">·</span>
            <span class="post__meta-item">작성일 {{ post.createdAt }}</span>

            <span class="post__meta-dot">·</span>
            <span class="post__meta-item">조회 {{ post.views }}</span>

            <span class="post__meta-dot">·</span>
            <span class="post__meta-item">댓글 {{ comments.length }}</span>
          </div>
        </div>

        <div class="post__header-actions">
          <button type="button" class="btn" @click="goList">
            목록
          </button>
          <template v-if="post.isMine">
            <button type="button" class="btn" @click="goEdit">
              수정
            </button>
            <button
              type="button"
              class="btn btn--danger"
              @click="handleDeletePost"
            >
              삭제
            </button>
          </template>
        </div>
      </header>

      <!-- 본문 내용 -->
      <article class="post__content">
        <pre class="post__content-text">{{ post.content }}</pre>
      </article>

      <!-- 댓글 영역 -->
      <section class="comments">
        <h2 class="comments__title">
          댓글
          <span class="comments__count">{{ comments.length }}</span>
        </h2>

        <!-- 댓글 작성 -->
        <div v-if="isAuthed" class="comments__form">
          <textarea
            v-model="newComment"
            class="comments__textarea"
            placeholder="댓글을 입력해주세요."
            rows="3"
          ></textarea>
          <div class="comments__form-actions">
            <button
              type="button"
              class="btn btn--primary"
              :disabled="!newComment.trim() || submittingComment"
              @click="handleCreateComment"
            >
              {{ submittingComment ? '등록 중...' : '댓글 등록' }}
            </button>
          </div>
        </div>
        <p v-else class="comments__hint">
          댓글 작성은 <strong>로그인 후</strong> 이용할 수 있습니다.
        </p>

        <!-- 댓글 리스트 -->
        <ul v-if="comments.length" class="comments__list">
          <li
            v-for="c in comments"
            :key="c.id"
            class="comments__item"
          >
            <div class="comments__item-header">
              <span class="comments__author">{{ c.author }}</span>
              <span class="comments__meta">{{ c.createdAt }}</span>
            </div>

            <!-- 일반 보기 -->
            <p
              v-if="editingCommentId !== c.id"
              class="comments__content"
            >
              {{ c.content }}
            </p>

            <!-- 수정 모드 -->
            <div v-else class="comments__edit">
              <textarea
                v-model="editCommentContent"
                class="comments__textarea"
                rows="3"
              ></textarea>
              <div class="comments__edit-actions">
                <button
                  type="button"
                  class="btn"
                  @click="cancelEditComment"
                >
                  취소
                </button>
                <button
                  type="button"
                  class="btn btn--primary"
                  :disabled="!editCommentContent.trim() || submittingComment"
                  @click="handleUpdateComment(c.id)"
                >
                  저장
                </button>
              </div>
            </div>

            <!-- 댓글 버튼 -->
            <div v-if="c.isMine" class="comments__item-actions">
              <button
                type="button"
                class="btn btn--xs"
                @click="startEditComment(c)"
              >
                수정
              </button>
              <button
                type="button"
                class="btn btn--xs btn--danger"
                @click="handleDeleteComment(c.id)"
              >
                삭제
              </button>
            </div>
          </li>
        </ul>

        <p v-else class="comments__empty">
          아직 댓글이 없습니다. 첫 댓글을 남겨보세요 ✨
        </p>
      </section>
    </div>
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

const postId = computed(() => route.params.id)

const loading = ref(true)
const error = ref('')
const post = ref(null)
const comments = ref([])

// 댓글 작성/수정 관련 상태
const newComment = ref('')
const submittingComment = ref(false)
const editingCommentId = ref(null)
const editCommentContent = ref('')

// 카테고리 라벨
const categories = [
  { value: 'grad',  label: '졸업 요건' },
  { value: 'course',label: '수강 / 시간표' },
  { value: 'major', label: '전과 / 복수전공' },
  { value: 'free',  label: '자유글' },
]

function categoryLabel(value) {
  const found = categories.find((c) => c.value === value)
  return found ? found.label : value
}

// 게시글 상세 불러오기
async function fetchPostDetail() {
  loading.value = true
  error.value = ''
  try {
    const res = await fetch(`/api/board/posts/${postId.value}`)
    if (!res.ok) {
      throw new Error('게시글을 불러오지 못했습니다.')
    }
    const data = await res.json()
    // 백엔드에서 위에서 설계한 형태로 내려준다고 가정
    post.value = {
      id: data.id,
      category: data.category,
      title: data.title,
      content: data.content,
      author: data.author,
      createdAt: data.createdAt,
      updatedAt: data.updatedAt,
      views: data.views,
      isMine: data.isMine,
    }
    comments.value = data.comments ?? []
  } catch (e) {
    console.error(e)
    error.value = e.message || '알 수 없는 오류가 발생했습니다.'
  } finally {
    loading.value = false
  }
}

// ===== 댓글 처리 =====
async function handleCreateComment() {
  const content = newComment.value.trim()
  if (!content) return
  submittingComment.value = true
  try {
    const res = await fetch(`/api/board/posts/${postId.value}/comments`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ content }),
    })
    if (!res.ok) throw new Error('댓글 등록에 실패했습니다.')
    const created = await res.json() // {id, author, content, createdAt, isMine}
    comments.value.push(created)
    newComment.value = ''
  } catch (e) {
    console.error(e)
    alert(e.message || '댓글 등록 중 오류가 발생했습니다.')
  } finally {
    submittingComment.value = false
  }
}

function startEditComment(comment) {
  editingCommentId.value = comment.id
  editCommentContent.value = comment.content
}

function cancelEditComment() {
  editingCommentId.value = null
  editCommentContent.value = ''
}

async function handleUpdateComment(commentId) {
  const content = editCommentContent.value.trim()
  if (!content) return
  submittingComment.value = true
  try {
    const res = await fetch(`/api/board/comments/${commentId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ content }),
    })
    if (!res.ok) throw new Error('댓글 수정에 실패했습니다.')

    // 성공 시 로컬 상태 갱신
    const target = comments.value.find((c) => c.id === commentId)
    if (target) target.content = content
    cancelEditComment()
  } catch (e) {
    console.error(e)
    alert(e.message || '댓글 수정 중 오류가 발생했습니다.')
  } finally {
    submittingComment.value = false
  }
}

async function handleDeleteComment(commentId) {
  if (!confirm('이 댓글을 삭제하시겠습니까?')) return
  try {
    const res = await fetch(`/api/board/comments/${commentId}`, {
      method: 'DELETE',
    })
    if (!res.ok) throw new Error('댓글 삭제에 실패했습니다.')
    comments.value = comments.value.filter((c) => c.id !== commentId)
  } catch (e) {
    console.error(e)
    alert(e.message || '댓글 삭제 중 오류가 발생했습니다.')
  }
}

// ===== 게시글 수정/삭제/이동 =====
function goList() {
  router.push('/board')
}

function goEdit() {
  router.push({ name: 'boardEdit', params: { id: post.value.id } })
}

async function handleDeletePost() {
  if (!confirm('게시글을 삭제하시겠습니까?')) return
  try {
    const res = await fetch(`/api/board/posts/${postId.value}`, {
      method: 'DELETE',
    })
    if (!res.ok) throw new Error('게시글 삭제에 실패했습니다.')
    alert('삭제가 완료되었습니다.')
    goList()
  } catch (e) {
    console.error(e)
    alert(e.message || '게시글 삭제 중 오류가 발생했습니다.')
  }
}

onMounted(() => {
  fetchPostDetail()
})
</script>

<style scoped>
.post {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* 로딩/에러 상태 */
.post__state {
  padding: 40px 0;
  text-align: center;
  color: #666;
}

.post__state--error {
  color: #b91c1c;
}

/* 카드 */
.post__card {
  border-radius: 12px;
  border: 1px solid #eee;
  background: #fff;
  padding: 20px 24px;
}

/* 헤더 */
.post__header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  border-bottom: 1px solid #f3f4f6;
  padding-bottom: 12px;
  margin-bottom: 16px;
}

.post__header-main {
  flex: 1 1 auto;
}

.post__title {
  margin: 0 0 8px;
  font-size: 20px;
  font-weight: 600;
}

.post__meta {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  align-items: center;
  font-size: 13px;
  color: #6b7280;
}

.post__meta-dot {
  margin: 0 4px;
}

.post__header-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

/* 본문 */
.post__content {
  margin-bottom: 24px;
}

.post__content-text {
  margin: 0;
  font-size: 14px;
  line-height: 1.7;
  white-space: pre-wrap;
  word-break: keep-all;
}

/* 배지 (카테고리) */
.badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 12px;
  background: #f3f4f6;
  color: #444;
}

.badge[data-cat='grad'] {
  background: #e5f0ff;
  color: #1f4fb8;
}

.badge[data-cat='course'] {
  background: #e8fff3;
  color: #15803d;
}

.badge[data-cat='major'] {
  background: #fff3e0;
  color: #b45309;
}

.badge[data-cat='free'] {
  background: #fdf2ff;
  color: #a21caf;
}

/* 댓글 */
.comments {
  border-top: 1px solid #f3f4f6;
  padding-top: 16px;
}

.comments__title {
  margin: 0 0 12px;
  font-size: 16px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.comments__count {
  font-size: 13px;
  color: #6b7280;
}

.comments__form {
  margin-bottom: 16px;
}

.comments__textarea {
  width: 100%;
  border-radius: 8px;
  border: 1px solid #ddd;
  padding: 8px 10px;
  font-size: 14px;
  resize: vertical;
  min-height: 80px;
  box-sizing: border-box;
}

.comments__textarea:focus {
  border-color: #1f7aec;
  outline: none;
  box-shadow: 0 0 0 1px rgba(31, 122, 236, 0.15);
}

.comments__form-actions,
.comments__edit-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 6px;
  gap: 6px;
}

.comments__hint {
  margin: 0 0 12px;
  font-size: 13px;
  color: #6b7280;
}

.comments__list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.comments__item {
  padding: 10px 0;
  border-top: 1px solid #f3f4f6;
}

.comments__item:first-of-type {
  border-top: none;
}

.comments__item-header {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  color: #6b7280;
  margin-bottom: 4px;
}

.comments__author {
  font-weight: 500;
  color: #374151;
}

.comments__content {
  margin: 0;
  font-size: 14px;
  line-height: 1.6;
  white-space: pre-wrap;
}

.comments__item-actions {
  margin-top: 4px;
  display: flex;
  gap: 4px;
}

/* 버튼들 */
.btn {
  border: 1px solid #ddd;
  background: #f7f7f7;
  padding: 6px 10px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 13px;
}

.btn--primary {
  background: #1f7aec;
  border-color: #1f7aec;
  color: #fff;
}

.btn--danger {
  border-color: #fecaca;
  background: #fee2e2;
  color: #b91c1c;
}

.btn--xs {
  padding: 4px 8px;
  font-size: 12px;
}

/* 반응형 */
@media (max-width: 640px) {
  .post__card {
    padding: 16px 14px;
  }

  .post__header {
    flex-direction: column;
    align-items: stretch;
  }

  .post__header-actions {
    justify-content: flex-end;
  }
}
</style>
