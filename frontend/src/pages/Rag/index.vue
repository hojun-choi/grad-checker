<!-- src/pages/Rag/index.vue -->
<template>
  <section class="rag">
    <!-- 상단 헤더 -->
    <header class="rag__header">
      <div>
        <h2>공지 검색AI</h2>
        <p class="rag__subtitle">
          질문에 맞춰 흩어진 학교·학과 공지를 AI가 분석하여 한 번에 찾아주는 검색 기능
        </p>
      </div>
    </header>

    <div class="rag__content">
      <!-- 검색 영역 -->
      <section class="rag__search-card">
        <form class="rag__search-form" @submit.prevent="handleSearch">
          <label class="rag__label" for="rag-query">
            공지나 규정, 절차를 검색해 보세요.
          </label>

          <div class="rag__input-row">
            <input
              id="rag-query"
              v-model="query"
              type="text"
              class="rag__input"
              :placeholder="placeholder"
              :disabled="isLoading"
            />
            <button
              type="submit"
              class="btn btn--primary"
              :disabled="isLoading || isQueryEmpty"
            >
              <span v-if="!isLoading">검색</span>
              <span v-else>검색 중...</span>
            </button>
          </div>

          <div class="rag__suggestions">
            <span class="rag__hint-label">예시 질문</span>
            <button
              v-for="(s, idx) in suggestions"
              :key="idx"
              type="button"
              class="rag__chip"
              @click="useSuggestion(s)"
              :disabled="isLoading"
            >
              {{ s }}
            </button>
          </div>
        </form>
      </section>

      <!-- 결과 영역 -->
      <section class="rag__result-card" v-if="hasResult">
        <!-- 로딩 중 -->
        <div v-if="isLoading" class="rag__loading">
          <span class="rag__spinner" aria-hidden="true" />
          <span>관련 공지를 모으는 중입니다. 잠시만 기다려 주세요...</span>
        </div>

        <!-- 에러 -->
        <div v-else-if="error" class="rag__error">
          {{ error }}
        </div>

        <!-- AI 답변 + 출처 -->
        <div v-else-if="result">
          <header class="rag__answer-header">
            <h3>요약 답변</h3>
            <p class="rag__answer-subtitle">
              검색된 공지와 규정을 바탕으로 정리한 내용입니다. 실제 공지 원문을 반드시 함께
              확인해 주세요.
            </p>
          </header>

          <div
            class="rag__answer-body"
            v-html="formattedAnswer"
          />

          <section
            v-if="topDocs.length"
            class="rag__sources"
          >
            <h4>참고한 공지 / 규정 (상위 {{ topDocs.length }}건)</h4>
            <ul class="rag__source-list">
              <li
                v-for="(doc, idx) in topDocs"
                :key="doc.id || idx"
                class="rag__source-item"
              >
                <a
                  :href="doc.metadata?.link || doc.id"
                  class="rag__source-title"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  {{ doc.metadata?.title || `문서 ${idx + 1}` }}
                </a>
                <span class="rag__source-meta">
                  <span v-if="doc.metadata?.department">
                    {{ formatDepartment(doc.metadata.department) }}
                  </span>
                  <span v-if="doc.metadata?.department && doc.metadata?.date">
                    ·
                  </span>
                  <span v-if="doc.metadata?.date">
                    {{ doc.metadata.date }}
                  </span>
                </span>
              </li>
            </ul>
          </section>
        </div>
      </section>

      <!-- 아직 검색 전일 때 안내 -->
      <section
        v-else
        class="rag__empty"
      >
        <p class="rag__empty-main">
          위 검색창에 궁금한 내용을 입력하면, 학교, 학과 공지를 기반으로
          AI가 한 번에 정리해서 알려줍니다.
        </p>
        <ul class="rag__empty-list">
          <li>“언제까지, 어떤 서류를 내야 하는지” 정리된 설명을 보고</li>
          <li>바로 아래에서 관련 공지 원문 링크를 함께 확인할 수 있습니다.</li>
          <li>이전 연도 공지도 함께 고려해서, 최신 학기 기준으로 안내해 줍니다.</li>
        </ul>
        <p class="rag__empty-tip">
          예: <strong>공학교육인증 포기 신청 방법</strong>,
          <strong>소프트웨어학부 졸업요건</strong>,
          <strong>복수전공 신청 일정</strong>
        </p>
        <p class="rag__empty-notice">
          ※ 실제 신청·변경 전에는 반드시 공지 원문과 u-SAINT 안내를 다시 확인해 주세요.
        </p>
      </section>
    </div>
  </section>
</template>

<script setup>
import { computed, ref } from 'vue'
import { api } from '../../api/api.js'

const query = ref('')
const isLoading = ref(false)
const error = ref('')
const result = ref(null)

// =========================
// 1) 학과 코드 → 한글 학과명 매핑
// =========================
const departmentDisplayNameMap = {
  // 인문대
  christian_studies: '기독교학과',
  korean_language: '국어국문학과',
  chinese_language: '중국어문학과',
  english_language: '영어영문학과',
  film_arts: '영화예술학과',
  french_language: '불어불문학과',
  german_language: '독어독문학과',
  history: '사학과',
  japanese_language: '일어일문학과',
  philosophy: '철학과',
  sports: '체육학과',

  // 자연대
  mathematics: '수학과',
  physics: '물리학과',
  chemistry: '화학과',
  statistics: '통계학과',
  biomedical_science: '생명과학과',

  // IT·공과·기타 단과대
  software: '소프트웨어학부',
  computer: '컴퓨터학부',
  infosec: '정보보호학과',
  ai_convergence: 'AI융합학부',
  electronic_engineering: '전자정보공학부',
  global_media: '글로벌미디어학부',
  chemical: '화학공학과',
  industrial: '산업·정보시스템공학과',
  electrical: '전기공학부',
  mechanical: '기계공학부',
  architecture: '건축학부',
  material: '신소재공학과',
  next_gen_semiconductor: '차세대반도체공학과',

  // 법과대
  globallaw: '국제법무학과',
  law: '법학과',

  // 사회과학대
  socialwelfare: '사회복지학부',
  publicadministration: '행정학부',
  politicalscience_internationalrelations: '정치외교학과',
  informationsociology: '정보사회학과',
  journalism_publicrelation_advertising: '언론홍보학과',
  lifelong_edu: '평생교육학과',

  // 경제·통상대
  economics: '경제학과',
  global_commerce: '글로벌통상학과',
  ecofinance: '금융경제학과',
  internationaltrade_transaction: '국제무역학과',

  // 경영대
  business_administration: '경영학부',
  venture_smallbusiness: '벤처중소기업학과',
  accounting: '회계학부',
  finance: '금융학부',
  venture_management: '벤처경영학과',
  innovation_management: '혁신경영학과',
  welfare_management: '복지경영학과',
  accounting_tex: '회계세무학과',

  // 기타
  liberal_study: '자유전공학부',
  baird: '베어드학부대학',
  ssu: '학교 학사공지',
}

// =========================
// 2) 학과 키워드 → 코드 매핑 (쿼리 확장용)
// =========================
// 한글 키워드(질문에 들어가는 단어) 기준으로 어떤 department 코드를 붙일지 정의
const departmentKeywordMap = {
  software: ['소프트웨어학부', '소프트웨어학과', '소프트웨어', '소웨', '솦'],
  computer: ['컴퓨터학부', '컴퓨터공학부', '컴공', '컴학'],
  infosec: ['정보보호학과', '정보'],
  ai_convergence: ['ai융합학부', 'ai융합', '에이아이융합학부', '애융'],

  industrial: [
    '산업정보시스템공학과',
    '산업·정보시스템공학과',
    '산업시스템공학과',
    '산업공학과',
    '산업·시스템공학과',
  ],
  chemical: ['화학공학과', '화공'],
  electrical: ['전기공학부', '전기공학과', '전기전자'],
  mechanical: ['기계공학부', '기계공학과'],
  architecture: ['건축학부', '건축학과'],
  material: ['신소재공학과', '신소재'],

  electronic_engineering: [
    '전자정보공학부',
    '전자정보공학과',
    '전자공학부',
    '전자공학과',
    'it융합전자',
  ],
  global_media: ['글로벌미디어학부', '글미'],
  next_gen_semiconductor: ['차세대반도체공학과', '차세대반도체'],

  christian_studies: ['기독교학과'],
  korean_language: ['국어국문학과', '국문학과'],
  chinese_language: ['중국어문학과', '중문과', '중문학과'],
  english_language: ['영어영문학과', '영문과', '영문학과'],
  film_arts: ['영화예술학과', '영화과'],
  french_language: ['불어불문학과', '불문과'],
  german_language: ['독어독문학과', '독문과'],
  history: ['사학과'],
  japanese_language: ['일어일문학과', '일문과'],
  philosophy: ['철학과'],
  sports: ['체육학과'],

  mathematics: ['수학과'],
  physics: ['물리학과'],
  chemistry: ['화학과'],
  statistics: ['통계학과'],
  biomedical_science: ['생명과학과', '생과'],

  globallaw: ['국제법무학과'],
  law: ['법학과'],

  socialwelfare: ['사회복지학부', '사회복지학과'],
  publicadministration: ['행정학부', '행정학과'],
  politicalscience_internationalrelations: ['정치외교학과', '정외과'],
  informationsociology: ['정보사회학과'],
  journalism_publicrelation_advertising: ['언론홍보학과', '언홍과'],
  lifelong_edu: ['평생교육학과'],

  economics: ['경제학과'],
  global_commerce: ['글로벌통상학과'],
  ecofinance: ['금융경제학과'],
  internationaltrade_transaction: ['국제무역학과'],

  business_administration: ['경영학부', '경영학과'],
  venture_smallbusiness: ['벤처중소기업학과'],
  accounting: ['회계학부', '회계학과'],
  finance: ['금융학부', '금융학과'],
  venture_management: ['벤처경영학과'],
  innovation_management: ['혁신경영학과'],
  welfare_management: ['복지경영학과'],
  accounting_tex: ['회계세무학과'],

  liberal_study: ['자유전공학부', '자전'],
  baird: ['베어드학부대학', '베어드대학'],
  ssu: ['학교공지', '학사공지', '숭실대학교 공지'],
}

// 예시 질문들
const suggestions = [
  '공학교육인증 포기 신청 방법',
  '소프트웨어학부 전과 신청',
  '복수전공 신청 방법',
  '휴학 절차',
]

const placeholder = '예: 공학교육인증 포기 신청'

const isQueryEmpty = computed(() => !query.value.trim())
const hasResult = computed(() => isLoading.value || !!result.value || !!error.value)

const topDocs = computed(() => {
  if (!result.value?.docs) return []
  // 너무 길어지지 않게 상위 6건만 노출
  return result.value.docs.slice(0, 6)
})

function escapeHtml(str) {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
}

// FastAPI answer는 마크다운 포맷이므로, 최소한의 포맷팅만 HTML로 변환
const formattedAnswer = computed(() => {
  if (!result.value?.answer) return ''
  let html = escapeHtml(result.value.answer)

  // 아주 간단한 마크다운 처리: **굵게**
  html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
  // 줄바꿈을 <br>로
  html = html.replace(/\n/g, '<br>')
  return html
})

// 학과 코드 → 한글 이름
function formatDepartment(dep) {
  if (!dep) return ''
  return departmentDisplayNameMap[dep] || dep
}

// 사용자가 입력한 문장 안에 학과명이 있으면
// 대응하는 department 코드를 뒤에 붙여서 쿼리 확장
function expandQueryWithDepartment(originalQuery) {
  const base = originalQuery
  const lower = originalQuery.toLowerCase()
  const tags = new Set()

  for (const [code, keywords] of Object.entries(departmentKeywordMap)) {
    if (
      keywords.some((kw) => originalQuery.includes(kw)) || // 한글 그대로 포함 검사
      keywords.some((kw) => lower.includes(kw.toLowerCase()))
    ) {
      tags.add(code)
    }
  }

  if (tags.size === 0) return base

  // 예: "소프트웨어학부 전과 신청" + " software" 같이 붙여서 보냄
  return `${base} ${Array.from(tags).join(' ')}`
}

function useSuggestion(text) {
  query.value = text
  // 예시 클릭하면 바로 검색까지
  handleSearch()
}

async function handleSearch() {
  if (isQueryEmpty.value || isLoading.value) return

  isLoading.value = true
  error.value = ''
  result.value = null

  try {
    const original = query.value.trim()
    const expandedQuery = expandQueryWithDepartment(original)

    const payload = {
      query: expandedQuery,
      top_k: 10,
    }

    // 스프링 백엔드를 통해 FastAPI(/rag/query)로 전달
    // 실제 HTTP 경로: /api/rag/query
    const res = await api.post('/rag/query', payload)

    result.value = res.data
  } catch (e) {
    console.error(e)
    error.value =
      '검색 중 오류가 발생했습니다. 잠시 후 다시 시도해 주세요.'
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.rag {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* 헤더 */
.rag__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 8px;
  margin-bottom: 2px;
}

.rag__header h2 {
  margin: 0;
  font-size: 1.2rem;
  font-weight: 700;
}

.rag__subtitle {
  margin: 4px 0 0;
  font-size: 0.85rem;
  color: #666;
}

/* 본문 래퍼 */
.rag__content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* 카드 공통 */
.rag__search-card,
.rag__result-card {
  background: #ffffff;
  border-radius: 12px;
  border: 1px solid #eee;
  padding: 14px 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
}

/* 검색 카드 아래 결과 카드/빈 카드가 어느 정도 높이를 갖게 */
.rag__result-card,
.rag__empty {
  min-height: 220px;
}

/* 검색 폼 */
.rag__search-form {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.rag__label {
  font-size: 0.9rem;
  font-weight: 600;
  margin-bottom: 2px;
}

.rag__input-row {
  display: flex;
  gap: 8px;
}

.rag__input {
  flex: 1;
  border-radius: 999px;
  border: 1px solid #ddd;
  padding: 10px 14px;
  font-size: 0.95rem;
  outline: none;
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
}

.rag__input:focus {
  border-color: #2563eb;
  box-shadow: 0 0 0 1px rgba(37, 99, 235, 0.15);
}

/* 버튼 스타일 */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0 14px;
  border-radius: 999px;
  border: 1px solid #ddd;
  background: #f7f7f7;
  font-size: 0.9rem;
  cursor: pointer;
  white-space: nowrap;
  height: 38px;
  transition: background 0.15s ease, border-color 0.15s ease,
    transform 0.05s ease;
}

.btn--primary {
  background: #2563eb;
  border-color: #2563eb;
  color: #ffffff;
}

.btn:disabled,
.btn.btn--primary:disabled {
  cursor: default;
  opacity: 0.6;
  transform: none;
}

.btn:not(:disabled):active {
  transform: translateY(1px);
}

/* 예시 질문 */
.rag__suggestions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px;
  margin-top: 4px;
  font-size: 0.8rem;
}

.rag__hint-label {
  color: #888;
  margin-right: 4px;
  font-weight: 500;
}

.rag__chip {
  padding: 4px 10px;
  border-radius: 999px;
  border: 1px solid #e2e8f0;
  background: #f8fafc;
  font-size: 0.8rem;
  cursor: pointer;
  transition: background 0.15s ease, border-color 0.15s ease;
}

.rag__chip:hover:not(:disabled) {
  background: #e0ecff;
  border-color: #bfdbfe;
}

/* 결과 영역 */
.rag__loading {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.9rem;
  color: #555;
}

.rag__spinner {
  width: 16px;
  height: 16px;
  border-radius: 999px;
  border: 2px solid #e5e7eb;
  border-top-color: #4b5563;
  animation: rag-spin 0.9s linear infinite;
}

@keyframes rag-spin {
  to {
    transform: rotate(360deg);
  }
}

.rag__answer-header h3 {
  margin: 0;
  font-size: 0.95rem;
  font-weight: 600;
}

.rag__answer-subtitle {
  margin: 4px 0 0;
  font-size: 0.8rem;
  color: #777;
}

.rag__answer-body {
  margin-top: 8px;
  font-size: 0.95rem;
  line-height: 1.7;
  color: #222;
  word-break: keep-all;
}

.rag__answer-body strong {
  font-weight: 600;
}

/* 출처 리스트 */
.rag__sources {
  margin-top: 14px;
  border-top: 1px dashed #e5e7eb;
  padding-top: 10px;
}

.rag__sources h4 {
  margin: 0 0 6px;
  font-size: 0.85rem;
  font-weight: 600;
}

.rag__source-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.rag__source-item {
  font-size: 0.85rem;
}

.rag__source-title {
  color: #2563eb;
  text-decoration: none;
}

.rag__source-title:hover {
  text-decoration: underline;
}

.rag__source-meta {
  margin-left: 4px;
  color: #9ca3af;
}

/* 초기 안내 */
.rag__empty {
  padding: 16px 18px;
  border-radius: 12px;
  border: 1px dashed #e5e7eb;
  background: #f9fafb;
  font-size: 0.9rem;
  color: #4b5563;
}

.rag__empty-main {
  margin-top: 0;
  margin-bottom: 6px;
}

.rag__empty-list {
  margin: 0 0 6px 1.1rem;
  padding: 0;
  font-size: 0.85rem;
}

.rag__empty-list li {
  margin-bottom: 2px;
}

.rag__empty-tip {
  margin-top: 4px;
}

.rag__empty-notice {
  margin-top: 6px;
  font-size: 0.8rem;
  color: #9ca3af;
}

/* 에러 메시지 */
.rag__error {
  padding: 10px 12px;
  border-radius: 8px;
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #b91c1c;
  font-size: 0.9rem;
}

/* 모바일 대응 */
@media (max-width: 640px) {
  .rag__header {
    flex-direction: column;
    align-items: flex-start;
  }

  .rag__input-row {
    flex-direction: column;
  }

  .btn {
    width: 100%;
  }
}
</style>
