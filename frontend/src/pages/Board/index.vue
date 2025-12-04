<template>
  <section class="board">
    <header class="board__header">
      <div>
        <h1>게시판</h1>
        <p class="board__subtitle">
          졸업 요건, 시간표, 전과/복수전공 등 정보를 서로 공유하는 공간
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
            @keyup.enter="fetchPosts"
          />
        </div>
      </div>
    </div>

    <p v-if="!isAuthed" class="board__hint">
      읽기는 누구나 가능하고,
      <strong>글쓰기/댓글은 로그인 후</strong> 이용할 수 있습니다.
    </p>

    <div class="board__list">
      <table v-if="posts.length" class="table">
        <thead>
          <tr>
            <th style="width:120px">게시판명</th>
            <th>제목</th>
            <th style="width:120px">작성자</th>
            <th style="width:140px">작성일</th>
            <th style="width:80px">조회</th>
            <th style="width:80px">댓글</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="post in posts" :key="post.id">
            <td>
              <span class="badge" :data-cat="getCategoryStyle(post.category)">
                {{ post.category }}
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
            <td>{{ formatDate(post.createdAt) }}</td>
            <td>{{ post.views }}</td>
            <td>{{ post.replies }}</td>
          </tr>
        </tbody>
      </table>

      <div v-else class="empty">
        <p>조건에 맞는 게시글이 없거나, 아직 등록된 글이 없습니다. ✨</p>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../../composables/useAuth.js'
import { api } from '../../api/api.js'
import { useToast } from 'vue-toastification'

const router = useRouter()
const toast = useToast()

// 로그인 여부
const { isAuthenticated } = useAuth()
const isAuthed = computed(() => isAuthenticated())

// 말머리(카테고리)
const categories = ref([
  { value: 'all', label: '전체' },
])

// 검색 / 필터 / 정렬 상태
const search = ref('')
const category = ref('all')
const sort = ref('latest')

const posts = ref([])

async function fetchPosts() {
  try {
    const params = {
      page: 0,
      size: 20,
      sortBy: sort.value,
    }

    if (category.value !== 'all') {
      params.boardName = category.value
    }
    if (search.value.trim()) {
      params.keyword = search.value.trim()
    }

    const response = await api.get('/board/posts', { params })
    posts.value = response.data.posts.content
    
    if (response.data.boardTypes) {
      const serverCategories = response.data.boardTypes.map(bt => ({
        value: bt.boardName, 
        label: bt.boardName
      }))
      categories.value = [{ value: 'all', label: '전체' }, ...serverCategories]
    }

  } catch (error) {
    console.error('게시글 목록 조회 실패:', error)
    // 목록 조회 실패는 너무 자주 뜨면 방해가 될 수 있으므로, 
    // 필요하다면 toast.error를 추가하되 여기서는 콘솔만 남겨둠.
  }
}

onMounted(() => {
  fetchPosts()
})

watch([category, sort], () => {
  fetchPosts()
})

function getCategoryStyle(boardName) {
  if (!boardName) return 'free'
  if (boardName.includes('졸업')) return 'grad'
  if (boardName.includes('수강') || boardName.includes('시간표')) return 'course'
  if (boardName.includes('전과') || boardName.includes('복수')) return 'major'
  return 'free'
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  return dateStr.replace('T', ' ').substring(0, 16)
}

function onClickWrite() {
  if (!isAuthed.value) {
    // alert 대신 warning toast 사용
    toast.warning('로그인 후 글쓰기가 가능합니다.\n상단 우측에서 로그인해주세요.')
    return
  }
  router.push({ name: 'boardWrite' }) 
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
  transition: all 0.2s;
}

.chip:hover {
  background: #eee;
}

.chip--active {
  background: #1f7aec;
  border-color: #1f7aec;
  color: #fff;
}

.chip--active:hover {
  background: #1a66c4;
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
  cursor: pointer;
}

.search input {
  border: 1px solid #ddd;
  border-radius: 999px;
  padding: 6px 14px;
  font-size: 13px;
  width: 180px;
  outline: none;
}

.search input:focus {
  border-color: #1f7aec;
}

/* 로그인 안내 */
.board__hint {
  font-size: 13px;
  color: #777;
  background: #f9f9f9;
  padding: 8px 12px;
  border-radius: 6px;
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
  min-width: 600px; /* 모바일에서 가로 스크롤 유도 */
}

th,
td {
  padding: 12px 16px;
  border-bottom: 1px solid #f1f1f1;
  text-align: left;
}

th {
  background: #fafafa;
  font-weight: 500;
  color: #555;
  white-space: nowrap;
}

td {
  color: #333;
}

/* 제목 셀: 길어지면 ... 처리 */
.title-cell {
  max-width: 200px;
}

.title-link {
  display: inline-block;
  max-width: 100%;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  color: #222;
  text-decoration: none;
  font-weight: 500;
}

.title-link:hover {
  text-decoration: underline;
  color: #1f7aec;
}

/* 말머리 배지 */
.badge {
  display: inline-block;
  padding: 3px 8px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 500;
  background: #f3f4f6;
  color: #444;
  white-space: nowrap;
}

/* data-cat 속성값에 따른 색상 (getCategoryStyle 함수 결과와 매칭) */
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
  padding: 60px 20px;
  text-align: center;
  color: #999;
  font-size: 15px;
}

/* 버튼 스타일 (홈 카드랑 비슷하게) */
.btn {
  border: 1px solid #ddd;
  background: #f7f7f7;
  padding: 8px 16px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s;
}

.btn:hover {
  filter: brightness(0.95);
}

.btn--primary {
  background: #1f7aec;
  border-color: #1f7aec;
  color: #fff;
}

.btn--primary:hover {
  background: #1a66c4;
}

.btn--disabled {
  opacity: 0.6;
  cursor: not-allowed;
  background: #eee;
  border-color: #ddd;
  color: #999;
}

/* 모바일 대응 */
@media (max-width: 640px) {
  .board__header {
    flex-direction: column;
    align-items: flex-start;
  }

  .board__controls {
    flex-direction: column-reverse;
    align-items: stretch;
  }

  .board__filters {
    width: 100%;
    justify-content: space-between;
  }
  
  .search input {
    width: 100%; /* 검색창 넓게 */
  }
  
  .title-cell {
    max-width: 140px; /* 모바일에서 제목 더 짧게 자르기 */
  }
}
</style>