<!-- src/pages/Rag/index.vue -->
<template>
  <section class="rag">
    <!-- 상단 헤더 -->
    <header class="rag__header">
      <div>
        <h1>RAG 검색</h1>
        <p class="rag__subtitle">
          학교·학과 공지, 규정 등을 기반으로 궁금한 내용을 검색할 수 있는 기능입니다.
        </p>
      </div>
    </header>

    <!-- 본문: 채팅 영역 + 입력 바 -->
    <div class="rag__shell">
      <!-- 메시지 영역 -->
      <div ref="messagesEl" class="rag__messages">
        <!-- 비어 있을 때 -->
        <div v-if="!messages.length" class="rag__empty">
          <p class="rag__empty-title">무엇이 궁금하신가요?</p>
          <p class="rag__empty-desc">
            예시 질문을 눌러보거나, 하단 입력창에 자유롭게 질문을 입력해보세요.
          </p>

          <div class="rag__suggest">
            <span class="rag__suggest-label">예시 질문</span>
            <div class="rag__suggest-list">
              <button
                v-for="s in suggestions"
                :key="s.id"
                class="chip chip--ghost"
                @click="fillFromSuggestion(s.text)"
              >
                {{ s.text }}
              </button>
            </div>
          </div>
        </div>

        <!-- 채팅 내역 -->
        <template v-else>
          <div
            v-for="msg in messages"
            :key="msg.id"
            class="chat-row"
            :class="{
              'chat-row--user': msg.role === 'user',
              'chat-row--assistant': msg.role === 'assistant'
            }"
          >
            <div
              class="bubble"
              :class="{
                'bubble--user': msg.role === 'user',
                'bubble--assistant': msg.role === 'assistant'
              }"
            >
              <p class="bubble__meta">
                <span class="bubble__who">
                  {{ msg.role === 'user' ? '나' : 'Graduation Checker' }}
                </span>
                <span class="bubble__time">{{ msg.time }}</span>
              </p>
              <p class="bubble__text">
                {{ msg.text }}
              </p>

              <!-- 참고한 문서 목록 (assistant일 때만) -->
              <div
                v-if="msg.role === 'assistant' && msg.sources?.length"
                class="bubble__sources"
              >
                <span class="bubble__sources-label">참고한 문서</span>
                <div class="bubble__sources-list">
                  <button
                    v-for="src in msg.sources"
                    :key="src.id"
                    type="button"
                    class="chip chip--source"
                  >
                    {{ src.label }}
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- 로딩 중일 때 (검색 중 버블) -->
          <div v-if="isLoading" class="chat-row chat-row--assistant">
            <div class="bubble bubble--assistant bubble--loading">
              <p class="bubble__meta">
                <span class="bubble__who">Graduation Checker</span>
              </p>
              <div class="dot-loading">
                <span></span><span></span><span></span>
              </div>
            </div>
          </div>
        </template>
      </div>

      <!-- 입력 영역 -->
      <form class="rag__input" @submit.prevent="handleSend">
        <textarea
          v-model="draft"
          class="rag__textarea"
          rows="1"
          placeholder="예: 23학번 AI융합 졸업요건에서 캡스톤디자인 필수인가요?"
          @keydown.enter.exact.prevent="handleSubmitShortcut"
          @keydown.ctrl.enter.prevent="handleEnter"
        ></textarea>

        <div class="rag__input-footer">
          <p class="rag__hint">
            Enter: 전송 · Ctrl + Enter: 줄바꿈
          </p>
          <button
            type="submit"
            class="send-btn"
            :disabled="!draft.trim() || isLoading"
          >
            <span class="send-btn__icon">↑</span>
          </button>
        </div>
      </form>
    </div>
  </section>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'

// 채팅 내역 (지금은 더미 데이터, 나중에 RAG 응답으로 교체)
const messages = ref([])

// 입력값
const draft = ref('')

// 로딩 상태
const isLoading = ref(false)

// 메시지 영역 ref (자동 스크롤)
const messagesEl = ref(null)

// 간단한 더미 시계 함수
function nowString() {
  const d = new Date()
  const hh = String(d.getHours()).padStart(2, '0')
  const mm = String(d.getMinutes()).padStart(2, '0')
  return `${hh}:${mm}`
}

// 예시 질문
const suggestions = [
  {
    id: 1,
    text: '23학번 AI융합 졸업요건에서 전공필수 몇 학점 들어야 하나요?',
  },
  {
    id: 2,
    text: '융특 → AI융합 전과했을 때, 전공기초 과목 인정은 어떻게 되나요?',
  },
  {
    id: 3,
    text: '23학번 기준으로 캡스톤디자인을 안 들으면 졸업이 불가능한가요?',
  },
]

// 예시 질문 클릭 시 입력창에 채워 넣기
function fillFromSuggestion(text) {
  draft.value = text
}

// 메시지 변경 시 스크롤 맨 아래로
watch(
  () => messages.value.length,
  () => {
    nextTick(() => {
      const el = messagesEl.value
      if (el) {
        el.scrollTop = el.scrollHeight
      }
    })
  }
)

// Ctrl+Enter → 줄바꿈
function handleEnter() {
  draft.value += '\n'
}

// Enter → 전송
function handleSubmitShortcut() {
  handleSend()
}

// 전송 버튼 / Enter
function handleSend() {
  const content = draft.value.trim()
  if (!content || isLoading.value) return

  // 사용자 메시지 추가
  messages.value.push({
    id: Date.now(),
    role: 'user',
    text: content,
    time: nowString(),
  })

  draft.value = ''
  isLoading.value = true

  // TODO: 여기에서 실제 RAG 검색 API 호출
  // ex) const res = await api.post('/api/rag/search', { query: content })

  // UI 전용 더미 응답
  const fakeAnswer =
    '여기에 RAG 검색 결과가 표시됩니다. 나중에 백엔드에서 가져온 답변으로 교체하면 됩니다.'

  const fakeSources = [
    {
      id: 's1',
      label: 'AI융합학과 학사요람 (2023년)',
    },
    {
      id: 's2',
      label: '졸업요건 안내 공지 (2024-02)',
    },
  ]

  messages.value.push({
    id: Date.now() + 1,
    role: 'assistant',
    text: fakeAnswer,
    time: nowString(),
    sources: fakeSources,
  })

  isLoading.value = false
}
</script>

<style scoped>
/* Pretendard: 오픈 라이선스 한글 폰트 (SIL OFL) */
@import url('https://cdn.jsdelivr.net/npm/pretendard@1.3.9/dist/web/static/pretendard.css');

.rag {
  display: flex;
  flex-direction: column;
  gap: 16px;
  width: 100%;
  font-family: 'Pretendard', 'Noto Sans KR', -apple-system, BlinkMacSystemFont,
    system-ui, 'Apple SD Gothic Neo', 'Segoe UI', sans-serif;
}

/* 헤더 */
.rag__header h1 {
  font-size: 22px;
  margin: 0 0 4px;
  font-weight: 700;
}

.rag__subtitle {
  margin: 0;
  color: #666;
  font-size: 14px;
  line-height: 1.5;
}

/* 외곽 셸
   - 화면 높이 기준으로 고정
   - 숫자(220px)는 상단 글로벌 헤더 + 페이지 제목/여백 + 하단 푸터를 대충 뺀 값이라
     필요하면 조금씩 조절해서 맞추면 됨.
*/
.rag__shell {
  margin-top: 4px;
  border-radius: 12px;
  border: 1px solid #eee;
  background: #fff;
  display: flex;
  flex-direction: column;
  height: calc(100vh - 220px);
  min-height: 320px;
  min-width: 0;
}

/* 메시지 영역: 여기만 스크롤 */
.rag__messages {
  flex: 1 1 auto;
  padding: 16px 16px 8px;
  overflow-y: auto;
  min-height: 0;
}

/* 빈 상태 */
.rag__empty {
  text-align: left;
  color: #666;
  font-size: 14px;
}

.rag__empty-title {
  margin: 0 0 4px;
  font-weight: 600;
  font-size: 15px;
  color: #333;
}

.rag__empty-desc {
  margin: 0 0 12px;
  line-height: 1.5;
}

.rag__suggest {
  margin-top: 8px;
}

.rag__suggest-label {
  font-size: 13px;
  color: #777;
}

.rag__suggest-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 6px;
}

/* 채팅 행 */
.chat-row {
  display: flex;
  margin-bottom: 10px;
}

.chat-row--user {
  justify-content: flex-end;
}

.chat-row--assistant {
  justify-content: flex-start;
}

/* 말풍선 */
.bubble {
  max-width: 70%;
  padding: 10px 12px;
  border-radius: 16px;
  font-size: 14px;
  line-height: 1.6;
  box-shadow: 0 1px 3px rgba(15, 23, 42, 0.06);
}

.bubble--user {
  background: #1f7aec;
  color: #fff;
  border-bottom-right-radius: 4px;
}

.bubble--assistant {
  background: #f5f7fb;
  color: #111827;
  border-bottom-left-radius: 4px;
}

.bubble__meta {
  display: flex;
  justify-content: space-between;
  margin: 0 0 4px;
  font-size: 11px;
  opacity: 0.8;
}

.bubble__who {
  font-weight: 600;
}

.bubble__text {
  margin: 0;
  white-space: pre-wrap;
  word-break: keep-all;
}

/* 참고 문서 영역 */
.bubble__sources {
  margin-top: 8px;
  padding-top: 6px;
  border-top: 1px dashed rgba(148, 163, 184, 0.6);
}

.bubble__sources-label {
  display: block;
  font-size: 11px;
  color: #6b7280;
  margin-bottom: 4px;
}

.bubble__sources-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

/* 로딩 버블 */
.bubble--loading {
  max-width: 120px;
}

.dot-loading {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.dot-loading span {
  width: 6px;
  height: 6px;
  border-radius: 999px;
  background: #4b5563;
  opacity: 0.4;
  animation: dot 1s infinite ease-in-out;
}

.dot-loading span:nth-child(2) {
  animation-delay: 0.15s;
}
.dot-loading span:nth-child(3) {
  animation-delay: 0.3s;
}

@keyframes dot {
  0%,
  80%,
  100% {
    transform: translateY(0);
    opacity: 0.4;
  }
  40% {
    transform: translateY(-3px);
    opacity: 1;
  }
}

/* 입력 영역 (아래 고정) */
.rag__input {
  border-top: 1px solid #eee;
  padding: 10px 12px 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.rag__textarea {
  width: 100%;
  border-radius: 10px;
  border: 1px solid #ddd;
  padding: 8px 10px;
  font-size: 14px;
  resize: none;
  max-height: 160px;
  min-height: 40px;
  box-sizing: border-box;
  font-family: inherit;
  line-height: 1.6;
}

.rag__textarea:focus {
  border-color: #1f7aec;
  outline: none;
  box-shadow: 0 0 0 1px rgba(31, 122, 236, 0.15);
}

.rag__input-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
}

.rag__hint {
  margin: 0;
  font-size: 11px;
  color: #9ca3af;
}

/* 예시 버튼/소스 태그 */
.chip {
  border-radius: 999px;
  padding: 4px 10px;
  font-size: 12px;
  border: 1px solid #e5e7eb;
  background: #f9fafb;
  cursor: pointer;
  font-family: inherit;
}

.chip--ghost {
  background: #f9fafb;
}

.chip--source {
  background: #eef2ff;
  border-color: #c7d2fe;
  color: #1d4ed8;
}

/* 전송 버튼 (동그란 원 + 위 화살표) */
.send-btn {
  width: 34px;
  height: 34px;
  border-radius: 999px;
  border: none;
  background: #1377f3;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 4px 8px rgba(37, 99, 235, 0.35);
  transition: transform 0.08s ease, box-shadow 0.08s ease, opacity 0.08s ease;
}

.send-btn__icon {
  color: #fff;
  font-size: 16px;
  font-weight: 600;
  transform: translateY(-1px);
}

.send-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 6px 12px rgba(37, 99, 235, 0.4);
}

.send-btn:active:not(:disabled) {
  transform: translateY(0);
  box-shadow: 0 3px 6px rgba(37, 99, 235, 0.3);
}

.send-btn:disabled {
  opacity: 0.4;
  cursor: default;
  box-shadow: none;
}

/* 모바일 대응 */
@media (max-width: 640px) {
  .rag__shell {
    height: calc(100vh - 260px); /* 모바일에서 조금 더 여유 */
  }

  .bubble {
    max-width: 82%;
  }

  .rag__input-footer {
    gap: 4px;
  }
}
</style>
