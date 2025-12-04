<template>
  <div class="page-container">
    <div v-if="loading" class="state-msg">
      <div class="spinner"></div>
      <p>게시글을 불러오는 중입니다...</p>
    </div>
    <div v-else-if="error" class="state-msg error">
      <p>{{ error }}</p>
      <button class="btn btn-secondary" @click="goList">목록으로 돌아가기</button>
    </div>

    <div v-else class="post-wrapper">
      <nav class="post-nav">
        <button type="button" class="nav-back-btn" @click="goList">
          <span class="icon">←</span> 목록으로
        </button>
      </nav>

      <main class="post-card">
        <header class="post-header">
          <div class="post-category">
            <span class="badge" :class="getCategoryClass(post.category)">
              {{ post.category }}
            </span>
          </div>
          <h1 class="post-title">{{ post.title }}</h1>
          
          <div class="post-meta">
            <div class="meta-left">
              <span class="author-name" :class="{'is-me': post.isMine}">
                {{ getDisplayName(post) }}
              </span>
              <span class="divider"></span>
              <span class="date">{{ formatDate(post.createdAt) }}</span>
            </div>
            <div class="meta-right">
              <span class="view-count">조회 {{ post.views }}</span>
              <span class="divider"></span>
              <span class="comment-count">댓글 {{ totalCommentCount }}</span>
            </div>
          </div>
        </header>

        <div class="post-divider"></div>

        <article class="post-body">
          <div class="post-content">{{ post.content }}</div>
        </article>

        <div class="post-actions" v-if="post.isMine">
          <button class="btn btn-outline" @click="goEdit">수정</button>
          <button class="btn btn-danger-outline" @click="handleDeletePost">삭제</button>
        </div>
      </main>

      <section class="comment-section">
        <h3 class="section-title">
          댓글 <span class="highlight">{{ totalCommentCount }}</span>
        </h3>

        <div class="comment-form-card" v-if="isAuthed">
          <div class="form-header">
            <span class="user-label">내 댓글 작성</span>
            <label class="checkbox-label">
              <input type="checkbox" v-model="newCommentIsAnonymous" />
              <span class="custom-check"></span> 익명
            </label>
          </div>
          <textarea
            v-model="newCommentContent"
            class="comment-input"
            placeholder="따뜻한 댓글을 남겨주세요."
            rows="3"
          ></textarea>
          <div class="form-footer">
            <button
              class="btn btn-primary"
              :disabled="!newCommentContent.trim() || submitting"
              @click="handleCreateComment(null)"
            >
              등록
            </button>
          </div>
        </div>
        <div v-else class="login-plz-box">
          <p>댓글을 작성하려면 <a @click="$router.push('/login')">로그인</a>이 필요합니다.</p>
        </div>

        <div class="comment-list">
          <div v-if="rootComments.length === 0" class="no-comments">
            아직 댓글이 없습니다. 첫 댓글의 주인공이 되어보세요!
          </div>

          <div 
            v-for="parent in rootComments" 
            :key="parent.id" 
            class="comment-group"
          >
            <div class="comment-item">
              <div class="comment-head">
                <div class="comment-info">
                  <span class="comment-author" 
                    :class="{
                      'is-author': parent.author === post.author && !parent.isAnonymous,
                      'is-me': parent.isMine
                    }"
                  >
                    {{ getDisplayName(parent) }}
                  </span>
                  <span class="comment-date">{{ formatDate(parent.createdAt) }}</span>
                </div>
                <div class="comment-opts" v-if="isAuthed">
                  <button class="text-btn" @click="toggleReplyForm(parent.id)">답글</button>
                  <template v-if="parent.isMine">
                    <button class="text-btn" @click="startEdit(parent)">수정</button>
                    <button class="text-btn delete" @click="handleDeleteComment(parent.id)">삭제</button>
                  </template>
                </div>
              </div>

              <div class="comment-body">
                <p v-if="canShowContent(parent)" v-show="editingId !== parent.id" class="comment-text">
                  {{ parent.content }}
                </p>
                <div v-else class="blur-content">
                  🔒 로그인 후 내용을 확인할 수 있습니다.
                </div>
                
                <div v-if="editingId === parent.id" class="edit-box">
                  <textarea v-model="editContent" class="edit-input"></textarea>
                  <div class="edit-btns">
                    <button class="btn btn-xs" @click="cancelEdit">취소</button>
                    <button class="btn btn-xs btn-primary" @click="handleUpdateComment(parent.id)">저장</button>
                  </div>
                </div>
              </div>
            </div>

            <div v-if="parent.children && parent.children.length > 0" class="replies-list">
              <div 
                v-for="child in parent.children" 
                :key="child.id" 
                class="comment-item reply-item"
              >
                <div class="reply-arrow">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <polyline points="9 10 4 15 9 20"></polyline>
                    <path d="M20 4v7a4 4 0 0 1-4 4H4"></path>
                  </svg>
                </div>
                
                <div class="reply-content-wrap">
                  <div class="comment-head">
                    <div class="comment-info">
                      <span class="comment-author" 
                        :class="{
                          'is-author': child.author === post.author && !child.isAnonymous,
                          'is-me': child.isMine
                        }"
                      >
                        {{ getDisplayName(child) }}
                      </span>
                      <span class="comment-date">{{ formatDate(child.createdAt) }}</span>
                    </div>
                    <div class="comment-opts" v-if="child.isMine">
                      <button class="text-btn" @click="startEdit(child)">수정</button>
                      <button class="text-btn delete" @click="handleDeleteComment(child.id)">삭제</button>
                    </div>
                  </div>

                  <div class="comment-body">
                    <p v-if="canShowContent(child)" v-show="editingId !== child.id" class="comment-text">
                      {{ child.content }}
                    </p>
                    <div v-else class="blur-content">
                      🔒 로그인 후 내용을 확인할 수 있습니다.
                    </div>

                    <div v-if="editingId === child.id" class="edit-box">
                      <textarea v-model="editContent" class="edit-input"></textarea>
                      <div class="edit-btns">
                        <button class="btn btn-xs" @click="cancelEdit">취소</button>
                        <button class="btn btn-xs btn-primary" @click="handleUpdateComment(child.id)">저장</button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div v-if="replyTargetId === parent.id" class="reply-form">
              <div class="reply-arrow-indicator">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <polyline points="9 10 4 15 9 20"></polyline>
                  <path d="M20 4v7a4 4 0 0 1-4 4H4"></path>
                </svg>
              </div>
              <div class="reply-input-wrap">
                <div class="form-header-sm">
                  <span class="sm-label">답글 작성</span>
                  <label class="checkbox-label sm">
                    <input type="checkbox" v-model="replyIsAnonymous" />
                    <span>익명</span>
                  </label>
                </div>
                <textarea
                  v-model="replyContent"
                  class="comment-input sm"
                  placeholder="답글 내용을 입력하세요."
                  rows="2"
                ></textarea>
                <div class="form-footer">
                  <button class="btn btn-xs" @click="replyTargetId = null">취소</button>
                  <button 
                    class="btn btn-xs btn-primary" 
                    :disabled="!replyContent.trim()" 
                    @click="handleCreateComment(parent.id)"
                  >
                    등록
                  </button>
                </div>
              </div>
            </div>

          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuth } from '../../composables/useAuth.js'
import { api } from '../../api/api.js'
import { useToast } from 'vue-toastification'

const route = useRoute()
const router = useRouter()
const { isAuthenticated } = useAuth()
const toast = useToast()

// --- State ---
const isAuthed = computed(() => isAuthenticated())
const postId = computed(() => route.params.id)
const loading = ref(true)
const error = ref('')
const post = ref({})
const rawComments = ref([]) 

// 작성/수정 State
const submitting = ref(false)

// 1. 새 댓글 (최상위)
const newCommentContent = ref('')
const newCommentIsAnonymous = ref(false)

// 2. 답글 (대댓글)
const replyTargetId = ref(null) 
const replyContent = ref('')
const replyIsAnonymous = ref(false)

// 3. 수정
const editingId = ref(null)
const editContent = ref('')

// --- Computed ---
const rootComments = computed(() => {
  if (!rawComments.value) return []
  const roots = rawComments.value.filter(c => !c.parentId)
  return roots.map(parent => {
    const children = rawComments.value.filter(c => c.parentId === parent.id)
    children.sort((a, b) => a.id - b.id)
    return { ...parent, children }
  })
})

const totalCommentCount = computed(() => rawComments.value.length)

// --- Methods ---

function getDisplayName(item) {
  return item.author
}

function canShowContent(item) {
  if (!isAuthed.value) return false
  if (item.content === null || item.content === undefined) return false
  return true
}

function getCategoryClass(catName) {
  if (!catName) return 'free'
  if (catName.includes('공지')) return 'notice'
  if (catName.includes('졸업') || catName.includes('진로')) return 'grad'
  if (catName.includes('장터')) return 'market'
  return 'default'
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  return dateStr.replace('T', ' ').slice(0, 16)
}

async function fetchPostDetail() {
  loading.value = true
  try {
    const res = await api.get(`/board/posts/${postId.value}`)
    const data = res.data
    post.value = {
      ...data,
      isMine: data.isMine ?? false,
      isAnonymous: data.isAnonymous ?? false
    }
    rawComments.value = data.comments || [] 
  } catch (e) {
    error.value = '게시글을 불러올 수 없습니다.'
    console.error(e)
    toast.error('게시글을 불러오는 중 문제가 발생했습니다.')
  } finally {
    loading.value = false
  }
}

async function handleCreateComment(parentId = null) {
  const isReply = !!parentId
  const content = isReply ? replyContent.value : newCommentContent.value
  const isAnonymous = isReply ? replyIsAnonymous.value : newCommentIsAnonymous.value

  if (!content.trim()) return

  submitting.value = true
  try {
    await api.post(`/board/posts/${postId.value}/comments`, {
      content,
      parentId,       
      isAnonymous     
    })

    if (isReply) {
      replyContent.value = ''
      replyIsAnonymous.value = false
      replyTargetId.value = null
    } else {
      newCommentContent.value = ''
      newCommentIsAnonymous.value = false
    }
    await fetchPostDetail()
    toast.success('댓글이 등록되었습니다.')
  } catch (e) {
    console.error(e)
    toast.error('댓글 등록에 실패했습니다.')
  } finally {
    submitting.value = false
  }
}

function toggleReplyForm(parentId) {
  if (replyTargetId.value === parentId) {
    replyTargetId.value = null
  } else {
    replyTargetId.value = parentId
    replyContent.value = ''
    replyIsAnonymous.value = false
  }
}

function startEdit(comment) {
  editingId.value = comment.id
  editContent.value = comment.content
}

function cancelEdit() {
  editingId.value = null
  editContent.value = ''
}

async function handleUpdateComment(commentId) {
  if (!editContent.value.trim()) return
  try {
    await api.put(`/board/comments/${commentId}`, { content: editContent.value })
    const target = rawComments.value.find(c => c.id === commentId)
    if (target) target.content = editContent.value
    toast.success('댓글이 수정되었습니다.')
    cancelEdit()
  } catch (e) {
    toast.error('댓글 수정에 실패했습니다.')
  }
}

async function handleDeleteComment(commentId) {
  if (!confirm('정말 삭제하시겠습니까?')) return
  try {
    await api.delete(`/board/comments/${commentId}`)
    rawComments.value = rawComments.value.filter(c => c.id !== commentId)
    toast.success('댓글이 삭제되었습니다.')
  } catch (e) {
    toast.error('댓글 삭제에 실패했습니다.')
  }
}

async function handleDeletePost() {
  if (!confirm('게시글을 삭제하시겠습니까? (삭제된 글은 복구할 수 없습니다)')) return
  try {
    await api.delete(`/board/posts/${postId.value}`)
    toast.success('게시글이 삭제되었습니다.')
    router.replace('/board')
  } catch (e) {
    console.error(e)
    toast.error('게시글 삭제에 실패했습니다.')
  }
}

function goList() {
  router.push('/board')
}

function goEdit() {
  router.push(`/board/${postId.value}/edit`)
}

onMounted(() => {
  fetchPostDetail()
})
</script>

<style scoped>
/* --- 기본 레이아웃 & 유틸리티 --- */
.page-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  color: #333;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}

.state-msg {
  text-align: center;
  padding: 60px 0;
  color: #666;
}
.spinner {
  width: 40px; height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

/* --- 버튼 스타일 --- */
.btn {
  padding: 8px 16px; border-radius: 6px; border: none;
  font-size: 14px; font-weight: 500; cursor: pointer; transition: all 0.2s;
}
.btn-primary { background: #3b82f6; color: white; }
.btn-primary:hover { background: #2563eb; }
.btn-primary:disabled { background: #93c5fd; cursor: not-allowed; }
.btn-secondary { background: #e5e7eb; color: #374151; }
.btn-secondary:hover { background: #d1d5db; }
.btn-outline { background: transparent; border: 1px solid #d1d5db; color: #374151; }
.btn-outline:hover { background: #f9fafb; border-color: #9ca3af; }
.btn-danger-outline { background: white; border: 1px solid #fecaca; color: #dc2626; }
.btn-danger-outline:hover { background: #fef2f2; }
.btn-xs { padding: 4px 10px; font-size: 12px; }

.text-btn {
  background: none; border: none; font-size: 12px; color: #6b7280;
  cursor: pointer; padding: 0; margin-left: 8px; text-decoration: underline;
}
.text-btn:hover { color: #374151; }
.text-btn.delete { color: #ef4444; }

/* --- 상단 네비게이션 --- */
.post-nav { margin-bottom: 20px; }
.nav-back-btn {
  background: none; border: none; font-size: 15px; color: #6b7280;
  cursor: pointer; display: flex; align-items: center; gap: 6px; padding: 8px 0;
}
.nav-back-btn:hover { color: #111; }

/* --- 게시글 카드 --- */
.post-card {
  background: white; border: 1px solid #e5e7eb; border-radius: 12px;
  padding: 40px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

.post-category { margin-bottom: 12px; }
.badge {
  display: inline-block; padding: 4px 10px; border-radius: 20px;
  font-size: 12px; font-weight: 600; background: #f3f4f6; color: #4b5563;
}
.badge.notice { background: #fff1f2; color: #be123c; }
.badge.grad { background: #eff6ff; color: #1d4ed8; }
.badge.market { background: #ecfccb; color: #4d7c0f; }

.post-title {
  font-size: 24px; font-weight: 700; color: #111827; margin: 0 0 16px; line-height: 1.4;
}

.post-meta {
  display: flex; justify-content: space-between; align-items: center;
  font-size: 14px; color: #6b7280;
}
.meta-left, .meta-right { display: flex; align-items: center; }
.author-name { font-weight: 600; color: #374151; }
.author-name.is-me { color: #2563eb; } 
.divider {
  display: inline-block; width: 1px; height: 12px; background: #d1d5db; margin: 0 10px;
}

.post-divider {
  height: 1px; background: #e5e7eb; margin: 24px 0 32px;
}
.post-body {
  min-height: 200px; font-size: 16px; line-height: 1.8; color: #374151;
}
.post-content { white-space: pre-wrap; word-wrap: break-word; }
.post-actions {
  margin-top: 40px; display: flex; justify-content: flex-end; gap: 8px;
}

/* --- 댓글 섹션 --- */
.comment-section { margin-top: 32px; padding-bottom: 60px; }
.section-title {
  font-size: 18px; font-weight: 700; margin-bottom: 16px;
  display: flex; align-items: center; gap: 6px;
}
.highlight { color: #3b82f6; }

/* 댓글 입력 카드 */
.comment-form-card {
  background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 8px;
  padding: 16px; margin-bottom: 30px;
}
.form-header { display: flex; justify-content: space-between; margin-bottom: 8px; }
.user-label { font-size: 14px; font-weight: 600; color: #4b5563; }
.checkbox-label {
  font-size: 13px; color: #4b5563; display: flex; align-items: center;
  gap: 6px; cursor: pointer;
}
.comment-input {
  width: 100%; border: 1px solid #d1d5db; border-radius: 6px; padding: 10px;
  font-size: 14px; resize: none; outline: none; background: white; box-sizing: border-box;
}
.comment-input:focus { border-color: #3b82f6; box-shadow: 0 0 0 2px rgba(59,130,246,0.1); }
.form-footer { margin-top: 10px; text-align: right; display: flex; justify-content: flex-end; gap: 8px; }

.login-plz-box {
  background: #f3f4f6; padding: 20px; text-align: center; border-radius: 8px;
  color: #6b7280; font-size: 14px; margin-bottom: 30px;
}
.login-plz-box a { color: #3b82f6; font-weight: 600; cursor: pointer; text-decoration: underline; }

/* 댓글 목록 */
.comment-list { display: flex; flex-direction: column; gap: 24px; }
.no-comments {
  text-align: center; padding: 40px; color: #9ca3af; background: #f9fafb; border-radius: 8px;
}

.comment-item { position: relative; }
.comment-head {
  display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;
}
.comment-info { display: flex; align-items: center; gap: 8px; font-size: 13px; }

.comment-author { font-weight: 700; color: #374151; }
.comment-author.is-author { color: #059669; background: #ecfdf5; padding: 2px 6px; border-radius: 4px; }
.comment-author.is-me { color: #2563eb; }

.comment-date { color: #9ca3af; font-size: 12px; }

.comment-body { font-size: 14px; color: #1f2937; line-height: 1.6; }
.comment-text { white-space: pre-wrap; word-break: break-all; }
.blur-content { color: #9ca3af; font-style: italic; filter: blur(0.5px); opacity: 0.8; }

/* 대댓글 */
.replies-list {
  margin-top: 12px; padding-left: 0;
  display: flex; flex-direction: column; gap: 12px;
}
.reply-item {
  display: flex; gap: 12px; margin-left: 20px;
}
.reply-arrow {
  color: #9ca3af; flex-shrink: 0; padding-top: 4px; width: 20px; height: 20px;
}
.reply-content-wrap {
  flex: 1; background: #f8fafc; padding: 16px; border-radius: 8px;
}

/* 답글 폼 */
.reply-form {
  margin-top: 12px; margin-left: 20px; display: flex; gap: 12px;
}
.reply-arrow-indicator { color: #3b82f6; flex-shrink: 0; padding-top: 4px; }
.reply-input-wrap {
  flex: 1; background: #fff; border: 1px solid #e5e7eb; padding: 12px; border-radius: 8px;
}
.form-header-sm { display: flex; justify-content: space-between; margin-bottom: 6px; }
.sm-label { font-size: 12px; font-weight: 600; color: #6b7280; }
.comment-input.sm { font-size: 13px; padding: 8px; min-height: 60px; }

.edit-box { margin-top: 8px; }
.edit-input { width: 100%; border: 1px solid #d1d5db; border-radius: 4px; padding: 8px; font-size: 13px; resize: vertical; box-sizing: border-box;}
.edit-btns { display: flex; justify-content: flex-end; gap: 4px; margin-top: 4px; }

@media (max-width: 640px) {
  .post-card { padding: 20px; }
  .post-title { font-size: 20px; }
  .reply-item { gap: 8px; margin-left: 10px; }
  .reply-form { margin-left: 10px; }
  .reply-content-wrap { padding: 12px; }
}
</style>