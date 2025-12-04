<template>
  <section class="planner">
    <header class="planner__header">
      <div class="planner__header-main">
        <h1>시간표·졸업 관리</h1>

        <div class="planner__subrow">
          <p class="planner__subtitle">
            내 시간표와 캘린더를 관리하고, 졸업 요건 충족 여부를 한눈에 확인하는 공간
          </p>

          <nav class="planner__tabs">
            <button
              v-for="tab in tabs"
              :key="tab.value"
              type="button"
              class="tab"
              :class="{ 'tab--active': activeTab === tab.value }"
              @click="activeTab = tab.value"
            >
              {{ tab.label }}
            </button>
          </nav>
        </div>
      </div>
    </header>

    <div class="planner__body">
      
      <div v-if="activeTab === 'timetable'" class="panel timetable-panel">
        
        <div class="tt-controls">
          <div class="tt-controls__left">
            <select v-model="currentYear" class="tt-select">
              <option :value="2025">2025학년도</option>
              <option :value="2024">2024학년도</option>
              <option :value="2023">2023학년도</option>
              <option :value="2022">2022학년도</option>
              <option :value="2021">2021학년도</option>
              <option :value="2020">2020학년도</option>
            </select>
            <select v-model="currentSemester" class="tt-select">
              <option :value="2">2학기</option>
              <option :value="'여름학기'">여름학기</option>
              <option :value="'겨울학기'">겨울학기</option>
              <option :value="1">1학기</option>
            </select>
          </div>

          <div class="tt-controls__right">
            <div class="tt-list">
               <button 
                v-for="tt in currentSemesterTimetables" 
                :key="tt.id"
                class="tt-pill"
                :class="{ 'tt-pill--active': selectedTimetableId === tt.id }"
                @click="selectedTimetableId = tt.id"
               >
                 <span 
                   class="star-icon" 
                   :class="{ 'star-icon--filled': tt.isPrimary }"
                   @click.stop="setPrimary(tt.id)"
                   title="대표 시간표 설정"
                 >
                   {{ tt.isPrimary ? '★' : '☆' }}
                 </span>
                 {{ tt.name }}
               </button>
               <button class="tt-add-btn" @click="createNewTimetable">+ 새 시간표</button>
             </div>
          </div>
        </div>

        <div class="tt-layout">
          
          <div class="tt-grid-container">
            <div class="tt-grid-header">
              <div class="tt-corner"></div> 
              <div v-for="day in days" :key="day" class="tt-day-label">{{ day }}</div>
            </div>

            <div class="tt-grid-body">
              <div class="tt-time-col">
                <div v-for="hour in visibleHours" :key="hour" class="tt-time-label">
                  {{ hour }}:00
                </div>
              </div>
              
              <div class="tt-cells" :style="{ height: (visibleHours.length * 60) + 'px' }">
                <div v-for="(day, idx) in days" :key="idx" class="tt-col-line"></div>
                
                <div 
                  v-for="hour in visibleHours" 
                  :key="'line-'+hour" 
                  class="tt-row-line"
                  :style="{ top: ((hour - startHour) * 60) + 'px' }"
                ></div>

                <div 
                  v-for="cls in currentTimetableData.classes" 
                  :key="cls.id"
                  class="tt-block"
                  :style="getClassStyle(cls)"
                >
                  <div class="tt-block__name">{{ cls.name }}</div>
                  <div class="tt-block__info">{{ cls.room }}</div>
                </div>
              </div>
            </div>
          </div>

          <aside class="tt-sidebar">
            <div class="search-box">
              <h3>수업 추가</h3>
              
              <div class="category-tags">
                <button 
                  v-for="cat in categories" 
                  :key="cat"
                  class="cat-btn"
                  :class="{ 'cat-btn--active': searchCategory === cat }"
                  @click="searchCategory = cat"
                >
                  {{ cat }}
                </button>
              </div>

              <div v-if="searchCategory === '전공'" class="major-filters">
                <select 
                  v-model="selectedCollege" 
                  class="filter-select"
                  :disabled="loadingMajors || !collegeOptions.length"
                >
                  <option value="">
                    {{ loadingMajors ? '데이터 불러오는 중...' : '단과대 선택' }}
                  </option>
                  <option v-for="c in collegeOptions" :key="c" :value="c">
                    {{ c }}
                  </option>
                </select>

                <select 
                  v-model="selectedFaculty" 
                  class="filter-select"
                  :disabled="!selectedCollege || !facultyOptions.length"
                >
                  <option value="">학부/학과 선택</option>
                  <option v-for="f in facultyOptions" :key="f" :value="f">
                    {{ f }}
                  </option>
                </select>

                <select 
                  v-model="selectedMajorName" 
                  class="filter-select"
                  :disabled="!selectedFaculty || !majorNameOptions.length"
                >
                  <option value="">전공 선택</option>
                  <option v-for="m in majorNameOptions" :key="m" :value="m">
                    {{ m }}
                  </option>
                </select>

                <select v-model="selectedGrade" class="filter-select">
                  <option value="">학년 전체</option>
                  <option value="1">1학년</option>
                  <option value="2">2학년</option>
                  <option value="3">3학년</option>
                  <option value="4">4학년</option>
                </select>
              </div>

              <div class="search-input-wrap">
                <input 
                  type="text" 
                  v-model="searchKeyword" 
                  placeholder="강의명, 교수님 검색"
                  @keyup.enter="searchClasses"
                />
                <button class="search-btn" @click="searchClasses">검색</button>
              </div>

              <div class="search-results">
                <p class="empty-msg">
                  <span v-if="searchCategory === '전공' && !selectedMajorName">
                    전공을 선택하면 강의 목록이 표시됩니다.
                  </span>
                  <span v-else-if="loadingMajors">
                    {{ currentYear }}학년도 전공 목록 로딩 중...
                  </span>
                  <span v-else>
                    검색 결과가 여기에 표시됩니다.
                  </span>
                </p>
              </div>
            </div>
          </aside>

        </div>
      </div>

      <div v-else-if="activeTab === 'calendar'" class="panel">
        <section class="panel__card">
          <h2 class="panel__title">내 캘린더</h2>
          <p class="panel__text">
            강의 일정뿐 아니라 과제 마감, 시험, 스터디 등 개인 일정을 함께 관리하는 캘린더입니다.
          </p>
          <ul class="panel__list">
            <li>주/월 단위 일정 보기</li>
            <li>강의 시간 자동 반영</li>
          </ul>
        </section>
      </div>

      <div v-else-if="activeTab === 'graduation'" class="panel">
        <div class="panel__grid">
          <section class="panel__card">
            <h2 class="panel__title">졸업 요건 요약</h2>
            <p class="panel__text">
              여기에서 전체 이수 학점, 전공/교양, 균형교양, 전필·필수 과목 등
              졸업에 필요한 요건을 한눈에 볼 수 있습니다.
            </p>
            <ul class="panel__list">
              <li>총 이수 학점 / 필요한 학점</li>
              <li>전공 필수·선택 / 교양 학점</li>
            </ul>
          </section>

          <section class="panel__card panel__card--accent">
            <h2 class="panel__title">이번 학기 계획과 연계</h2>
            <p class="panel__text">
              시간표·캘린더에서 설정한 이번 학기 수강 계획을 바탕으로,
              졸업 요건에 얼마나 가까워졌는지 체크할 수 있습니다.
            </p>
          </section>
        </div>
      </div>

    </div>
  </section>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useAuth } from '../../composables/useAuth.js'
import { api } from '../../api/api.js'

const { isAuthenticated } = useAuth()

/* 메인 탭 관리 */
const tabs = [
  { value: 'timetable', label: '내 시간표' },
  { value: 'calendar', label: '내 캘린더' },
  { value: 'graduation', label: '졸업 요건' },
]
const activeTab = ref('timetable')

/* =========================================
   시간표(Timetable) 관련 로직
   ========================================= */

// 1. 상태 관리
// 학년도가 바뀌면 전공 데이터도 새로 불러와야 함
const currentYear = ref(2025)
const currentSemester = ref(1)
const selectedTimetableId = ref(1)

// 2. 검색 및 필터 관련 상태
const categories = ['전공', '교필', '교선', '채플', '교직', '융전']
const searchCategory = ref('전공')
const searchKeyword = ref('')

// 전공 데이터 상태
const majors = ref([])
const loadingMajors = ref(false)

// 선택된 필터 값
const selectedCollege = ref('')
const selectedFaculty = ref('')
const selectedMajorName = ref('')
const selectedGrade = ref('')

// Computed: 3단 드롭다운 필터링
const collegeOptions = computed(() => {
  const set = new Set()
  for (const m of majors.value) {
    if (m.college) set.add(m.college)
  }
  return Array.from(set)
})

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

// Watchers: 상위 필터 변경 시 하위 초기화
watch(selectedCollege, () => {
  selectedFaculty.value = ''
  selectedMajorName.value = ''
})
watch(selectedFaculty, () => {
  selectedMajorName.value = ''
})

// Watcher: 학년도(currentYear) 변경 감지 -> 전공 목록 새로 로드
watch(currentYear, () => {
  // 학년도가 바뀌면 기존 선택값들은 해당 연도에 없을 수도 있으므로 초기화 추천
  selectedCollege.value = ''
  loadMajors()
})

// 3. API 호출: 전공 목록 불러오기 (동적 파라미터 적용)
async function loadMajors() {
  loadingMajors.value = true
  try {
    // currentYear.value를 사용하여 해당 연도 데이터 로드
    const { data } = await api.get('/majors/history', {
      params: { 
        year: currentYear.value, 
        category: '학부전공' 
      },
    })
    majors.value = Array.isArray(data) ? data : []
  } catch (e) {
    console.error('전공 목록 로딩 실패:', e)
    majors.value = []
  } finally {
    loadingMajors.value = false
  }
}

// 4. 초기 로드
onMounted(() => {
  // 초기 currentYear(2025) 기준으로 로드됨
  loadMajors()
})


/* =========================================
   시간표 그리드 & 데이터 로직 (기존 유지)
   ========================================= */
const days = ['월', '화', '수', '목', '금']

const allTimetables = ref([
  {
    id: 1,
    year: 2025,
    semester: 1,
    name: '시간표 1',
    isPrimary: true,
    classes: [
      { id: 101, day: 0, start: 9.5, end: 11.0, name: '자료구조', room: '숭덕 301' },
      { id: 102, day: 2, start: 13.0, end: 15.0, name: '알고리즘', room: '형남 102' },
      { id: 103, day: 4, start: 18.0, end: 20.0, name: '야간교양', room: '온라인' },
    ]
  },
  {
    id: 2,
    year: 2025,
    semester: 1,
    name: '공강확보용',
    isPrimary: false,
    classes: []
  }
])

const currentSemesterTimetables = computed(() => {
  return allTimetables.value.filter(
    t => t.year === currentYear.value && t.semester === currentSemester.value
  )
})

const currentTimetableData = computed(() => {
  return allTimetables.value.find(t => t.id === selectedTimetableId.value) || { classes: [] }
})

const startHour = computed(() => {
  const classes = currentTimetableData.value.classes
  if (!classes.length) return 9
  const minStart = Math.min(...classes.map(c => Math.floor(c.start)))
  return Math.min(9, minStart)
})

const endHour = computed(() => {
  const classes = currentTimetableData.value.classes
  if (!classes.length) return 18
  const maxEnd = Math.max(...classes.map(c => Math.ceil(c.end)))
  return Math.max(18, maxEnd)
})

const visibleHours = computed(() => {
  const hours = []
  for (let i = startHour.value; i < endHour.value; i++) {
    hours.push(i)
  }
  return hours
})

function setPrimary(id) {
  currentSemesterTimetables.value.forEach(t => {
    t.isPrimary = (t.id === id)
  })
}

function createNewTimetable() {
  const newId = Date.now()
  allTimetables.value.push({
    id: newId,
    year: currentYear.value,
    semester: currentSemester.value,
    name: `새 시간표 ${currentSemesterTimetables.value.length + 1}`,
    isPrimary: false,
    classes: []
  })
  selectedTimetableId.value = newId
}

function searchClasses() {
  console.log('검색 조건:', {
    category: searchCategory.value,
    year: currentYear.value, // 검색 시 현재 선택된 학년도도 함께 전송 가능
    semester: currentSemester.value,
    college: selectedCollege.value,
    faculty: selectedFaculty.value,
    major: selectedMajorName.value,
    grade: selectedGrade.value,
    keyword: searchKeyword.value
  })
}

function getClassStyle(cls) {
  const hourHeight = 60
  const colWidth = 100 / 5
  const top = (cls.start - startHour.value) * hourHeight
  const height = (cls.end - cls.start) * hourHeight
  const left = cls.day * colWidth

  return {
    top: `${top}px`,
    height: `${height}px`,
    left: `${left}%`,
    width: `${colWidth}%`
  }
}
</script>

<style scoped>
/* 공통 레이아웃 */
.planner {
  display: flex;
  flex-direction: column;
  gap: 16px;
  width: 100%;
}

.planner__header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  width: 100%;
}

.planner__header-main {
  display: flex;
  flex-direction: column;
  gap: 6px;
  width: 100%;
}

.planner__header h1 {
  font-size: 22px;
  margin: 0;
}

.planner__subrow {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: nowrap;
  width: 100%;
}

.planner__subtitle {
  margin: 0;
  color: #666;
  font-size: 14px;
  flex: 1 1 auto;
}

/* 탭 네비게이션 */
.planner__tabs {
  display: inline-flex;
  border-radius: 999px;
  padding: 3px;
  background: #f3f4f6;
  gap: 4px;
  flex-shrink: 0;
}

.tab {
  border: none;
  background: transparent;
  padding: 6px 14px;
  border-radius: 999px;
  font-size: 13px;
  cursor: pointer;
  color: #6b7280;
}

.tab--active {
  background: #1f7aec;
  color: #fff;
  box-shadow: 0 2px 4px rgba(37, 99, 235, 0.3);
}

.planner__body {
  border-radius: 12px;
  border: 1px solid #eee;
  background: #fff;
  padding: 18px 20px;
  min-height: 600px;
}

/* =========================================
   [CSS] 시간표 전용 스타일
   ========================================= */

.tt-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid #eee;
}

.tt-controls__left {
  display: flex;
  gap: 8px;
}

.tt-select {
  padding: 6px 10px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  background: #fff;
  cursor: pointer;
}

.tt-controls__right {
  display: flex;
  align-items: center;
}

.tt-list {
  display: flex;
  gap: 6px;
}

.tt-pill {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  border: 1px solid #e5e7eb;
  border-radius: 20px;
  background: #fff;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.tt-pill:hover { background: #f9fafb; }

.tt-pill--active {
  border-color: #1f7aec;
  color: #1f7aec;
  background: #eff6ff;
  font-weight: 600;
}

.tt-add-btn {
  padding: 6px 10px;
  border: 1px dashed #d1d5db;
  border-radius: 20px;
  background: transparent;
  font-size: 12px;
  cursor: pointer;
  color: #6b7280;
}
.tt-add-btn:hover { border-color: #1f7aec; color: #1f7aec; }

.star-icon {
  font-size: 16px;
  color: #d1d5db;
  cursor: pointer;
  line-height: 1;
}
.star-icon--filled { color: #fbbf24; }

/* 2. 레이아웃 (그리드 : 사이드바 비율 조정) */
.tt-layout {
  display: flex;
  gap: 24px;
  align-items: flex-start;
  height: 100%;
}

/* 왼쪽: 그리드 영역 (Flex 2) */
.tt-grid-container {
  flex: 2;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.tt-grid-header {
  display: flex;
  background: #f9fafb;
  border-bottom: 1px solid #e5e7eb;
  height: 40px;
}

.tt-corner {
  width: 50px;
  flex-shrink: 0;
  border-right: 1px solid #e5e7eb;
}

.tt-day-label {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 600;
  color: #374151;
  border-right: 1px solid #e5e7eb;
}
.tt-day-label:last-child { border-right: none; }

.tt-grid-body {
  display: flex;
  position: relative;
  overflow-y: auto;
}

.tt-time-col {
  width: 50px;
  flex-shrink: 0;
  background: #fff;
  border-right: 1px solid #e5e7eb;
}

.tt-time-label {
  height: 60px;
  font-size: 11px;
  color: #9ca3af;
  text-align: right;
  padding-right: 6px;
  transform: translateY(-50%);
  display: flex;
  align-items: flex-start;
  justify-content: flex-end;
  padding-top: 4px;
}

.tt-cells {
  flex: 1;
  position: relative;
  background: #fff;
}

.tt-col-line {
  position: absolute;
  top: 0; bottom: 0;
  width: 20%;
  border-right: 1px solid #f3f4f6;
  pointer-events: none;
}
.tt-col-line:nth-child(1) { left: 0; }
.tt-col-line:nth-child(2) { left: 20%; }
.tt-col-line:nth-child(3) { left: 40%; }
.tt-col-line:nth-child(4) { left: 60%; }
.tt-col-line:nth-child(5) { left: 80%; border-right: none; }

.tt-row-line {
  position: absolute;
  left: 0; right: 0;
  height: 1px;
  background: #f3f4f6;
  pointer-events: none;
}

.tt-block {
  position: absolute;
  background: #e0e7ff;
  border-left: 3px solid #6366f1;
  padding: 4px;
  overflow: hidden;
  font-size: 12px;
  border-radius: 2px;
  box-shadow: 0 1px 2px rgba(0,0,0,0.1);
  z-index: 10;
}

.tt-block__name {
  font-weight: 700;
  color: #3730a3;
  margin-bottom: 2px;
}
.tt-block__info { color: #4338ca; font-size: 11px; }

/* 오른쪽: 사이드바 (수업 추가 - Flex 1) */
.tt-sidebar {
  flex: 1;
  min-width: 340px;
  border-left: 1px solid #eee;
  padding-left: 24px;
  display: flex;
  flex-direction: column;
}

.search-box h3 {
  font-size: 18px;
  font-weight: 600;
  margin: 0 0 16px;
}

.category-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 16px;
}

.cat-btn {
  padding: 8px 14px;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  background: #fff;
  font-size: 13px;
  cursor: pointer;
  color: #4b5563;
  transition: all 0.2s;
}
.cat-btn:hover { background: #f9fafb; border-color: #d1d5db; }
.cat-btn--active {
  background: #1f7aec;
  color: white;
  border-color: #1f7aec;
}

/* 전공 선택 드롭다운 스타일 */
.major-filters {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 12px;
  background: #f8fafc;
  padding: 12px;
  border-radius: 8px;
  border: 1px solid #f1f5f9;
}

.filter-select {
  width: 100%;
  padding: 10px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  background: #fff;
  &:disabled {
    background: #f3f4f6;
    color: #9ca3af;
    cursor: not-allowed;
  }
}

.search-input-wrap {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}

.search-input-wrap input {
  flex: 1;
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
}

.search-btn {
  padding: 0 16px;
  background: #374151;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
}
.search-btn:hover { background: #1f2937; }

.search-results {
  flex: 1;
  min-height: 300px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #fafafa;
}
.empty-msg { font-size: 14px; color: #9ca3af; }

/* 기존 패널 스타일 */
.panel { width: 100%; }
.panel__grid { display: grid; grid-template-columns: minmax(0, 1.2fr) minmax(0, 1fr); gap: 16px; }
.panel__card { border-radius: 10px; border: 1px solid #eef0f4; padding: 14px 16px; background: #fafbff; }
.panel__card--accent { background: #f5f3ff; border-color: #e0e7ff; }
.panel__title { margin: 0 0 8px; font-size: 16px; font-weight: 600; }
.panel__text { margin: 0 0 8px; font-size: 14px; color: #4b5563; line-height: 1.6; }
.panel__list { margin: 0 0 8px; padding-left: 18px; font-size: 13px; color: #4b5563; }
.panel__list li + li { margin-top: 2px; }

/* 모바일 대응 */
@media (max-width: 900px) {
  .tt-layout {
    flex-direction: column;
  }
  .tt-grid-container {
    flex: 1 1 auto;
    width: 100%;
  }
  .tt-sidebar {
    width: 100%;
    min-width: 0;
    flex: 1 1 auto;
    border-left: none;
    padding-left: 0;
    border-top: 1px solid #eee;
    padding-top: 20px;
  }
}

@media (max-width: 768px) {
  .planner__header { flex-direction: column; align-items: flex-start; }
  .planner__subrow { flex-direction: column; align-items: flex-start; }
  .planner__tabs { align-self: flex-start; }
  .panel__grid { grid-template-columns: minmax(0, 1fr); }
  .tt-controls { flex-direction: column; align-items: flex-start; gap: 10px; }
  .tt-list { flex-wrap: wrap; }
}
</style>