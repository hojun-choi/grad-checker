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
            @keyup.enter="fetchPosts"
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
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../../composables/useAuth.js'
import { api } from '../../api/api.js'

const router = useRouter()

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
    // 백엔드 PostListResponse 구조: { posts: { content: [], ... }, boardTypes: [] }
    posts.value = response.data.posts.content
    
    // 카테고리 목록 업데이트 (전체 + 서버에서 받은 목록)
    const serverCategories = response.data.boardTypes.map(bt => ({
      value: bt.boardName, // boardName이 식별자로 쓰인다고 가정 (예: 'grad', 'course' 등)
      label: bt.boardName, // 화면 표시 이름도 boardName 사용 (필요 시 별도 필드 확인)
    }))
    categories.value = [{ value: 'all', label: '전체' }, ...serverCategories]

  } catch (error) {
    console.error('게시글 목록 조회 실패:', error)
  }
}

onMounted(() => {
  fetchPosts()
})

// 필터 변경 시 재조회
watch([category, sort], () => {
  fetchPosts()
})

// 검색어 엔터 처리 등을 위해 별도 함수로 빼거나 watch로 처리 가능
// 여기서는 간단히 watch로 처리 (디바운싱 없으면 입력마다 요청가니 주의, 일단은 엔터 칠 때만 하려면 @keyup.enter="fetchPosts" 권장)
// 기존 UI에 검색 버튼이 없으므로, 입력 후 엔터치면 재조회되도록 수정하는 게 좋음.
// 일단은 computed filteredPosts 로직을 제거하고 서버 사이드 필터링으로 전환했으므로
// filteredPosts 대신 posts를 바로 사용해야 함.

// 필터 + 검색 + 정렬 적용된 최종 리스트
// 필터 + 검색 + 정렬 적용된 최종 리스트
// 서버 사이드 페이징/필터링을 사용하므로 computed 제거하고 posts를 직접 사용
const filteredPosts = computed(() => posts.value)

function categoryLabel(value) {
  const found = categories.value.find((c) => c.value === value)
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
