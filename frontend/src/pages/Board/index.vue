<!-- src/pages/Board/index.vue -->
<template>
  <section class="board">
    <!-- 상단 헤더 -->
    <header class="board__header">
      <div>
        <h1>게시판</h1>
        <p class="board__subtitle">
          졸업 요건, 시간표, 전과/복수전공 등 정보를 서로 공유하는 공간입니다.<br>
          열람은 누구나, 글쓰기/댓글은 로그인 후 이용 가능합니다.
        </p>
      </div>

      <button
        class="btn btn--primary"
        :class="{ 'btn--disabled': !isAuthed }"
        @click="onClickWrite"
      >
        글 쓰기
      </button>
    </header>

    <!-- 필터 / 검색 영역 -->
    <div class="board__controls">
      <div class="chips">
        <button
          v-for="cat in categories"
          :key="cat.value"
          class="chip"
          :class="{ 'chip--active': category === cat.value }"
          @click="category = cat.value"
        >
          {{ cat.label }}
        </button>
      </div>

      <div class="board__filters">
        <select v-model="sort" class="select">
          <option value="latest">최신순</option>
          <option value="popular">조회순</option>
        </select>

        <div class="search">
          <input
            v-model="search"
            type="search"
            placeholder="제목 / 작성자 검색"
          />
        </div>
      </div>
    </div>

    <!-- 로그인 안내 -->
    <p v-if="!isAuthed" class="board__hint">
      읽기는 누구나 가능하고,
      <strong>글쓰기/댓글은 로그인 후</strong> 이용할 수 있습니다.
    </p>

    <!-- 게시글 리스트 -->
    <div class="board__list">
      <table v-if="filteredPosts.length" class="table">
        <thead>
          <tr>
            <th style="width:120px">게시판명</th>
            <th>제목</th>
            <th style="width:120px">작성자</th>
            <th style="width:120px">작성일</th>
            <th style="width:80px">조회</th>
            <th style="width:80px">댓글</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="post in filteredPosts" :key="post.id">
            <td>
              <span class="badge" :data-cat="post.category">
                {{ categoryLabel(post.category) }}
              </span>
            </td>
            <td class="title-cell">
              <RouterLink
                :to="`/board/posts/${post.id}`"
                class="title-link"
              >
                {{ post.title }}
              </RouterLink>
            </td>
            <td>{{ post.author }}</td>
            <td>{{ post.createdAt }}</td>
            <td>{{ post.views }}</td>
            <td>{{ post.replies }}</td>
          </tr>
        </tbody>
      </table>

      <div v-else class="empty">
        <p>아직 등록된 글이 없습니다. 첫 글의 주인공이 되어주세요 ✨</p>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../../composables/useAuth.js'

const router = useRouter()

// 로그인 여부
const { isAuthenticated } = useAuth()
const isAuthed = computed(() => isAuthenticated())

// 말머리(카테고리)
const categories = [
  { value: 'all',   label: '전체' },
  { value: 'grad',  label: '졸업 요건' },
  { value: 'course',label: '수강 / 시간표' },
  { value: 'major', label: '전과 / 복수전공' },
  { value: 'free',  label: '자유글' },
]

// 검색 / 필터 / 정렬 상태
const search = ref('')
const category = ref('all')
const sort = ref('latest')

// 일단은 더미 데이터로 목록 구성 (나중에 API 연동만 갈아끼우면 됨)
const posts = ref([
  {
    id: 1,
    category: 'grad',
    title: '23학번 AI융합 졸업요건 정리표 공유합니다',
    author: '익명',
    createdAt: '2025-11-11',
    views: 128,
    replies: 4,
  },
  {
    id: 2,
    category: 'course',
    title: '4학년 1학기 시간표 한 번만 봐주세요ㅠ',
    author: '익명2',
    createdAt: '2025-11-09',
    views: 96,
    replies: 7,
  },
  {
    id: 3,
    category: 'major',
    title: '융특 → AI융합 전과 경험 공유 & 질문 받습니다',
    author: '익명3',
    createdAt: '2025-11-05',
    views: 210,
    replies: 9,
  },
  {
    id: 4,
    category: 'free',
    title: 'DB응용 기말 대비 스터디 같이 하실 분?',
    author: '익명4',
    createdAt: '2025-11-03',
    views: 75,
    replies: 2,
  },
])

// 필터 + 검색 + 정렬 적용된 최종 리스트
const filteredPosts = computed(() => {
  let list = posts.value.slice()

  if (category.value !== 'all') {
    list = list.filter((p) => p.category === category.value)
  }

  const q = search.value.trim().toLowerCase()
  if (q) {
    list = list.filter((p) =>
      p.title.toLowerCase().includes(q) ||
      p.author.toLowerCase().includes(q)
    )
  }

  if (sort.value === 'latest') {
    // createdAt이 'YYYY-MM-DD' 문자열이라면 이 정도 정렬이면 충분
    list.sort((a, b) => (a.createdAt < b.createdAt ? 1 : -1))
  } else if (sort.value === 'popular') {
    list.sort((a, b) => b.views - a.views)
  }

  return list
})

function categoryLabel(value) {
  const found = categories.find((c) => c.value === value)
  return found ? found.label : value
}

function onClickWrite() {
  if (!isAuthed.value) {
    alert('로그인 후 글쓰기가 가능합니다. 상단 우측에서 로그인 버튼을 눌러주세요.')
    return
  }
  router.push({ name: 'boardWrite' }) // 밑에서 라우트 이름 지정할 거임
}
</script>

<style scoped>
.board {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* 헤더 */
.board__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.board__header h1 {
  font-size: 22px;
  margin: 0 0 4px;
}

.board__subtitle {
  margin: 0;
  color: #666;
  font-size: 14px;
}

/* 상단 컨트롤 */
.board__controls {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
}

.chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.chip {
  border: 1px solid #ddd;
  padding: 4px 10px;
  border-radius: 999px;
  background: #f7f7f7;
  font-size: 13px;
  cursor: pointer;
  color: #555;
}

.chip--active {
  background: #1f7aec;
  border-color: #1f7aec;
  color: #fff;
}

.board__filters {
  display: flex;
  align-items: center;
  gap: 8px;
}

.select {
  border: 1px solid #ddd;
  border-radius: 999px;
  padding: 6px 10px;
  font-size: 13px;
  background: #fff;
}

.search input {
  border: 1px solid #ddd;
  border-radius: 999px;
  padding: 6px 10px;
  font-size: 13px;
}

/* 로그인 안내 */
.board__hint {
  font-size: 13px;
  color: #777;
}

/* 리스트 래퍼 */
.board__list {
  border: 1px solid #eee;
  border-radius: 12px;
  background: #fff;
  overflow-x: auto;
}

/* 테이블 */
.table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

th,
td {
  padding: 10px 12px;
  border-bottom: 1px solid #f1f1f1;
  text-align: left;
}

th {
  background: #fafafa;
  font-weight: 500;
  color: #555;
}

.title-cell {
  max-width: 0;
}

.title-link {
  display: inline-block;
  max-width: 100%;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  color: #222;
  text-decoration: none;
}

.title-link:hover {
  text-decoration: underline;
}

/* 말머리 배지 */
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

/* 빈 상태 */
.empty {
  padding: 24px 16px;
  text-align: center;
  color: #777;
  font-size: 14px;
}

/* 버튼 스타일 (홈 카드랑 비슷하게) */
.btn {
  border: 1px solid #ddd;
  background: #f7f7f7;
  padding: 8px 12px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
}

.btn--primary {
  background: #1f7aec;
  border-color: #1f7aec;
  color: #fff;
}

.btn--disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

/* 모바일 대응 */
@media (max-width: 640px) {
  .board__header {
    flex-direction: column;
    align-items: flex-start;
  }

  .board__filters {
    width: 100%;
    justify-content: flex-end;
  }
}
</style>
