<!-- src/views/Schedule/index.vue -->
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
      <!-- ===================== 시간표 탭 ===================== -->
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
              <option :value="'2학기'">2학기</option>
              <option :value="'여름학기'">여름학기</option>
              <option :value="'겨울학기'">겨울학기</option>
              <option :value="'1학기'">1학기</option>
            </select>
          </div>

          <div class="tt-controls__right">
            <div class="tt-list">
              <button
                v-for="tt in currentSemesterTimetables"
                :key="tt.id"
                class="tt-pill"
                :class="{ 'tt-pill--active': selectedTimetableId === tt.id }"
                @click="onSelectTimetable(tt.id)"
              >
                <span
                  class="star-icon"
                  :class="{ 'star-icon--filled': tt.primary }"
                  @click.stop="setPrimary(tt.id)"
                  title="대표 시간표 설정"
                >
                  {{ tt.primary ? '★' : '☆' }}
                </span>
                {{ tt.name }}
              </button>
              <button class="tt-add-btn" @click="createNewTimetable">
                + 새 시간표
              </button>
            </div>
          </div>
        </div>

        <div class="tt-layout">
          <!-- 왼쪽: 시간표 그리드 -->
          <div class="tt-grid-container">
            <div class="tt-grid-header">
              <div class="tt-corner"></div>
              <div v-for="day in days" :key="day" class="tt-day-label">
                {{ day }}
              </div>
            </div>

            <div class="tt-grid-body">
              <div class="tt-time-col">
                <div
                  v-for="hour in visibleHours"
                  :key="hour"
                  class="tt-time-label"
                >
                  {{ hour }}:00
                </div>
              </div>

              <div
                class="tt-cells"
                :style="{ height: visibleHours.length * 60 + 'px' }"
              >
                <!-- 세로 라인 -->
                <div
                  v-for="(day, idx) in days"
                  :key="idx"
                  class="tt-col-line"
                ></div>

                <!-- 가로 라인 -->
                <div
                  v-for="hour in visibleHours"
                  :key="'line-' + hour"
                  class="tt-row-line"
                  :style="{ top: (hour - startHour) * 60 + 'px' }"
                ></div>

                <!-- 수업 블록 -->
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

          <!-- 오른쪽: 수업 검색 사이드바 -->
          <aside class="tt-sidebar">
            <div class="search-box">
              <h3>수업 추가</h3>

              <!-- 상단 카테고리 탭 -->
              <div class="category-tags">
                <button
                  v-for="cat in categories"
                  :key="cat"
                  class="cat-btn"
                  :class="{ 'cat-btn--active': searchCategory === cat }"
                  @click="changeCategory(cat)"
                >
                  {{ cat }}
                </button>
              </div>

              <!-- 전공 선택 필터 (전공인 경우에만) -->
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

              <!-- 교선 영역 필터 (교선인 경우에만) -->
              <div v-else-if="searchCategory === '교선'" class="major-filters">
                <select v-model="selectedElectiveDomain" class="filter-select">
                  <option value="">교양 영역 전체</option>
                  <option
                    v-for="opt in electiveDomainOptions"
                    :key="opt"
                    :value="opt"
                  >
                    {{ opt }}
                  </option>
                </select>
              </div>

              <!-- 융합전공 필터 (융전인 경우) -->
              <div v-else-if="searchCategory === '융전'" class="major-filters">
                <select v-model="selectedIntegratedMajorTt" class="filter-select">
                  <option value="">융합전공 선택</option>
                  <option
                    v-for="m in integratedMajors"
                    :key="getTtMajor(m)"
                    :value="getTtMajor(m)"
                  >
                    {{ getMajorName(m) }}
                  </option>
                </select>
              </div>

              <!-- 연계전공 필터 (연전인 경우) -->
              <div v-else-if="searchCategory === '연전'" class="major-filters">
                <select v-model="selectedLinkedMajorTt" class="filter-select">
                  <option value="">연계전공 선택</option>
                  <option
                    v-for="m in linkedMajors"
                    :key="getTtMajor(m)"
                    :value="getTtMajor(m)"
                  >
                    {{ getMajorName(m) }}
                  </option>
                </select>
              </div>

              <!-- 검색창 -->
              <div class="search-input-wrap">
                <input
                  type="text"
                  v-model="searchKeyword"
                  placeholder="강의명, 교수님 검색"
                  @keyup.enter="searchClasses"
                />
                <button
                  class="search-btn"
                  @click="searchClasses"
                  :disabled="loadingLectures"
                >
                  {{ loadingLectures ? '검색 중...' : '검색' }}
                </button>
              </div>

              <!-- 검색 결과 영역 -->
              <div class="search-results">
                <!-- 결과 없음 -->
                <p class="empty-msg" v-if="!lectures.length">
                  <span v-if="searchCategory === '전공' && !selectedMajorName">
                    전공을 선택하면 강의 목록이 표시됩니다.
                  </span>
                  <span v-else-if="loadingMajors && searchCategory === '전공'">
                    {{ currentYear }}학년도 전공 목록 로딩 중...
                  </span>
                  <span v-else-if="loadingLectures">
                    강의 목록을 불러오는 중입니다...
                  </span>
                  <span v-else>
                    검색 결과가 여기에 표시됩니다.
                  </span>
                </p>

                <!-- 결과 리스트 -->
                <div v-else class="search-list">
                  <div class="search-list__summary">
                    총 {{ lectures.length }}개의 강의가 불러와졌습니다.
                  </div>
                  <ul class="search-list__items">
                    <li
                      v-for="lec in lectures"
                      :key="lec.id + '-' + (lec.meetingDay || '') + '-' + (lec.startTime || '')"
                      class="search-item"
                    >
                      <div class="search-item__info">
                        <div class="search-item__title">
                          {{ lec.courseTitle }}
                          <span class="search-item__code">({{ lec.courseCode }})</span>
                        </div>
                        <div class="search-item__meta">
                          <span>{{ lec.instructorName }}</span>

                          <!-- 여러 시간·요일을 한 항목에 합쳐서 표시 -->
                          <span v-if="lec.slots && lec.slots.length">
                            ·
                            <span
                              v-for="(slot, idx) in lec.slots"
                              :key="idx"
                            >
                              <span v-if="idx > 0"> / </span>
                              {{ slot.meetingDay }}
                              {{ slot.startTime }}~{{ slot.endTime }}
                            </span>
                          </span>

                          <!-- 강의실은 대표 한 개만 (첫 번째 슬롯 기준) -->
                          <span
                            v-if="lec.slots && lec.slots.length && lec.slots[0].buildingRoom"
                          >
                            · {{ lec.slots[0].buildingRoom }}
                          </span>

                          <span>
                            · {{ lec.courseCredits }}학점
                          </span>
                        </div>
                      </div>

                      <button
                        class="add-btn"
                        :disabled="!selectedTimetableId || addingLecture"
                        @click="addLectureToTimetable(lec)"
                      >
                        {{ selectedTimetableId ? '시간표에 추가' : '시간표 선택 필요' }}
                      </button>
                    </li>
                  </ul>
                </div>
              </div>
            </div>
          </aside>
        </div>
      </div>

      <!-- ===================== 캘린더 탭 ===================== -->
      <div v-else-if="activeTab === 'calendar'" class="panel">
        <section class="panel__card">
          <h2 class="panel__title">내 캘린더</h2>
          <p class="panel__text">
            강의 일정뿐 아니라 과제 마감, 시험, 스터디 등 개인 일정을 함께 관리하는
            캘린더입니다.
          </p>
          <ul class="panel__list">
            <li>주/월 단위 일정 보기</li>
            <li>강의 시간 자동 반영</li>
          </ul>
        </section>
      </div>

      <!-- ===================== 졸업 요건 탭 ===================== -->
      <div v-else-if="activeTab === 'graduation'" class="panel">
        <div class="panel__grid">
          <section class="panel__card">
            <h2 class="panel__title">졸업 요건 요약</h2>
            <p class="panel__text">
              여기에서 전체 이수 학점, 전공/교양, 균형교양, 전필·필수 과목 등 졸업에
              필요한 요건을 한눈에 볼 수 있습니다.
            </p>
            <ul class="panel__list">
              <li>총 이수 학점 / 필요한 학점</li>
              <li>전공 필수·선택 / 교양 학점</li>
            </ul>
          </section>

          <section class="panel__card panel__card--accent">
            <h2 class="panel__title">이번 학기 계획과 연계</h2>
            <p class="panel__text">
              시간표·캘린더에서 설정한 이번 학기 수강 계획을 바탕으로, 졸업 요건에
              얼마나 가까워졌는지 체크할 수 있습니다.
            </p>
          </section>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useToast } from 'vue-toastification'
import { useAuth } from '../../composables/useAuth.js'
import { api } from '../../api/api.js'

const { isAuthenticated } = useAuth()
const toast = useToast()

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
const currentYear = ref(2025)
const currentSemester = ref('1학기')
const selectedTimetableId = ref(null)

// 서버에서 가져온 내 모든 시간표
const allTimetables = ref([])
const loadingTimetables = ref(false)
const loadingTimetableDetail = ref(false)

// 2. 검색 및 필터 관련 상태
const categories = ['전공', '교필', '교선', '채플', '융전', '연전', '교직']
const searchCategory = ref('전공')
const searchKeyword = ref('')

// 전공(학부전공) 데이터 상태
const majors = ref([])
const loadingMajors = ref(false)

// 융합전공 / 연계전공 데이터 상태
const integratedMajors = ref([]) // category = '융합전공'
const linkedMajors = ref([]) // category = '연계전공'
const loadingIntegratedMajors = ref(false)
const loadingLinkedMajors = ref(false)

// 전공 필터
const selectedCollege = ref('')
const selectedFaculty = ref('')
const selectedMajorName = ref('')
const selectedGrade = ref('')

// 교선(교양 선택) 도메인 필터
const electiveDomainOptions = [
  `['20,'21~'22]공동체/리더십,숭실품성-인성과리더십`,
  `['20,'21~'22]공동체/리더십,숭실품성-자기계발과진로탐색`,
  `['20,'21~'22]의사소통/글로벌,기초역량-한국어의사소통`,
  `['20,'21~'22]의사소통/글로벌,기초역량-국제어문`,
  `['20,'21~'22]창의/융합,균형교양-문학·예술`,
  `['20,'21~'22]창의/융합,균형교양-역사·철학·종교`,
  `['20,'21~'22]창의/융합,균형교양-정치·경제·경영`,
  `['20,'21~'22]창의/융합,균형교양-사회·문화·심리`,
  `['20,'21~'22]창의/융합,균형교양-자연과학·공학·기술`,
  `['23이후]인간·언어`,
  `['23이후]문화·예술`,
  `['23이후]사회·정치·경제`,
  `['23이후]과학·기술`,
  `['23이후]자기개발·진로탐색`,
]
const selectedElectiveDomain = ref('')

// 융합전공 / 연계전공에서 선택한 tt_major 값
const selectedIntegratedMajorTt = ref('')
const selectedLinkedMajorTt = ref('')

// 강의 목록
const lectures = ref([])
const loadingLectures = ref(false)
const addingLecture = ref(false)

/* ---------- majors 공통 헬퍼 ---------- */
const getMajorName = (m) => m?.majorName ?? m?.major_name ?? m?.name ?? ''
const getTtMajor = (m) =>
  m?.ttMajor ?? m?.tt_major ?? m?.majorName ?? m?.major_name ?? ''

/* ---------- 전공(학부전공) 필터용 computed ---------- */
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
    if (
      m.college === selectedCollege.value &&
      m.faculty === selectedFaculty.value &&
      getMajorName(m)
    ) {
      set.add(getMajorName(m))
    }
  }
  return Array.from(set)
})

// 상위 필터 변경 시 하위 초기화
watch(selectedCollege, () => {
  selectedFaculty.value = ''
  selectedMajorName.value = ''
})
watch(selectedFaculty, () => {
  selectedMajorName.value = ''
})

/* ---------- 카테고리 변경 시 초기화 ---------- */
function changeCategory(cat) {
  searchCategory.value = cat
  lectures.value = []

  if (cat !== '전공') {
    selectedCollege.value = ''
    selectedFaculty.value = ''
    selectedMajorName.value = ''
    selectedGrade.value = ''
  }
  if (cat !== '교선') {
    selectedElectiveDomain.value = ''
  }
  if (cat !== '융전') {
    selectedIntegratedMajorTt.value = ''
  }
  if (cat !== '연전') {
    selectedLinkedMajorTt.value = ''
  }
}

// "['20,'21~'22]공동체/리더십,숭실품성-자기계발과진로탐색"
//  → "공동체/리더십,숭실품성-자기계발과진로탐색"
function normalizeDomain(label) {
  if (!label) return ''
  const m = label.match(/^\[[^\]]*](.*)$/)
  return m ? m[1].trim() : label
}
/* ---------- 학년도/학기 변경 시 로딩 ---------- */
watch(currentYear, () => {
  selectedCollege.value = ''
  loadMajors()
  loadIntegratedMajors()
  loadLinkedMajors()
  loadTimetables()
})

watch(currentSemester, () => {
  loadTimetables()
})

/* ---------- 선택된 시간표 ID 변경 시 상세 로드 ---------- */
watch(selectedTimetableId, (newId) => {
  if (newId) {
    loadTimetableDetail(newId)
  }
})

/* =========================================
   /majors/history 관련 API
   ========================================= */

// 학부전공
async function loadMajors() {
  loadingMajors.value = true
  try {
    const { data } = await api.get('/majors/history', {
      params: {
        year: currentYear.value,
        category: '학부전공',
      },
    })
    majors.value = Array.isArray(data) ? data : []
  } catch (e) {
    console.error('전공 목록 로딩 실패:', e)
    majors.value = []
    toast.error('전공 목록을 불러오지 못했습니다.')
  } finally {
    loadingMajors.value = false
  }
}

// 융합전공
async function loadIntegratedMajors() {
  loadingIntegratedMajors.value = true
  try {
    const { data } = await api.get('/majors/history', {
      params: {
        year: currentYear.value,
        category: '융합전공',
      },
    })
    integratedMajors.value = Array.isArray(data) ? data : []
  } catch (e) {
    console.error('융합전공 목록 로딩 실패:', e)
    integratedMajors.value = []
  } finally {
    loadingIntegratedMajors.value = false
  }
}

// 연계전공
async function loadLinkedMajors() {
  loadingLinkedMajors.value = true
  try {
    const { data } = await api.get('/majors/history', {
      params: {
        year: currentYear.value,
        category: '연계전공',
      },
    })
    linkedMajors.value = Array.isArray(data) ? data : []
  } catch (e) {
    console.error('연계전공 목록 로딩 실패:', e)
    linkedMajors.value = []
  } finally {
    loadingLinkedMajors.value = false
  }
}

/* =========================================
   내 시간표 API 연동
   ========================================= */

async function loadTimetables() {
  loadingTimetables.value = true
  try {
    const { data } = await api.get('/user-timetables', {
      params: {
        year: currentYear.value,
        semester: currentSemester.value,
      },
    })

    const list = Array.isArray(data) ? data : []
    allTimetables.value = list.map((tt) => ({
      ...tt,
      classes: tt.classes || [],
    }))

    const primary = allTimetables.value.find((t) => t.primary)
    const first = allTimetables.value[0]

    if (primary) {
      selectedTimetableId.value = primary.id
    } else if (first) {
      selectedTimetableId.value = first.id
    } else {
      selectedTimetableId.value = null
    }
  } catch (e) {
    console.error('시간표 목록 로딩 실패:', e)
    allTimetables.value = []
    selectedTimetableId.value = null
    toast.error('시간표 목록을 불러오지 못했습니다.')
  } finally {
    loadingTimetables.value = false
  }
}

async function loadTimetableDetail(timetableId) {
  if (!timetableId) return
  loadingTimetableDetail.value = true
  try {
    const { data } = await api.get(`/user-timetables/${timetableId}`)
    const idx = allTimetables.value.findIndex((t) => t.id === timetableId)
    if (idx !== -1) {
      allTimetables.value[idx] = {
        ...allTimetables.value[idx],
        ...data,
        classes: Array.isArray(data.classes) ? data.classes : [],
      }
    }
  } catch (e) {
    console.error('시간표 상세 로딩 실패:', e)
  } finally {
    loadingTimetableDetail.value = false
  }
}

async function setPrimary(id) {
  try {
    await api.patch(`/user-timetables/${id}/primary`)
    allTimetables.value = allTimetables.value.map((t) => ({
      ...t,
      primary: t.id === id,
    }))
    toast.success('대표 시간표가 변경되었습니다.')
  } catch (e) {
    console.error('대표 시간표 설정 실패:', e)
    toast.error('대표 시간표 설정에 실패했습니다.')
  }
}

async function createNewTimetable() {
  try {
    const payload = {
      year: currentYear.value,
      semester: currentSemester.value,
      name: `새 시간표 ${currentSemesterTimetables.value.length + 1}`,
    }
    const { data } = await api.post('/user-timetables', payload)
    const created = {
      ...data,
      classes: data.classes || [],
    }
    allTimetables.value.push(created)
    selectedTimetableId.value = created.id
    toast.success('새 시간표가 생성되었습니다.')
  } catch (e) {
    console.error('새 시간표 생성 실패:', e)
    toast.error('새 시간표 생성에 실패했습니다. 다시 시도해 주세요.')
  }
}

function onSelectTimetable(id) {
  selectedTimetableId.value = id
}

/* =========================================
   시간표 그리드 관련 computed
   ========================================= */

const days = ['월', '화', '수', '목', '금']

const currentSemesterTimetables = computed(() => {
  return allTimetables.value.filter(
    (t) => t.year === currentYear.value && t.semester === currentSemester.value,
  )
})

const currentTimetableData = computed(() => {
  if (!selectedTimetableId.value) {
    return { classes: [] }
  }
  return (
    allTimetables.value.find((t) => t.id === selectedTimetableId.value) || {
      classes: [],
    }
  )
})

const startHour = computed(() => {
  const classes = currentTimetableData.value.classes
  if (!classes.length) return 9
  const minStart = Math.min(...classes.map((c) => Math.floor(c.start)))
  return Math.min(9, minStart)
})

const endHour = computed(() => {
  const classes = currentTimetableData.value.classes
  if (!classes.length) return 18
  const maxEnd = Math.max(...classes.map((c) => Math.ceil(c.end)))
  return Math.max(18, maxEnd)
})

const visibleHours = computed(() => {
  const hours = []
  for (let i = startHour.value; i < endHour.value; i++) {
    hours.push(i)
  }
  return hours
})

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
    width: `${colWidth}%`,
  }
}

/* =========================================
   강의 검색 API 연동
   ========================================= */

async function searchClasses() {
  loadingLectures.value = true
  lectures.value = []

  try {
    const commonParams = {
      year: currentYear.value,
      semester: currentSemester.value,
    }

    let url = ''
    const params = { ...commonParams }

    switch (searchCategory.value) {
      case '전공': {
        url = '/lectures/major'

        if (
          !selectedCollege.value ||
          !selectedFaculty.value ||
          !selectedMajorName.value
        ) {
          toast.warning('단과대 / 학부 / 전공을 모두 선택해 주세요.')
          loadingLectures.value = false
          return
        }

        const selectedMajor = majors.value.find(
          (m) =>
            m.college === selectedCollege.value &&
            m.faculty === selectedFaculty.value &&
            getMajorName(m) === selectedMajorName.value,
        )

        if (!selectedMajor) {
          toast.error('선택한 전공 정보를 찾을 수 없습니다.')
          loadingLectures.value = false
          return
        }

        params.ttMajor = getTtMajor(selectedMajor)
        break
      }
      case '교필':
        url = '/lectures/core'
        break
      case '교선':
        url = '/lectures/elective'
        if (selectedElectiveDomain.value) {
          params.domain = normalizeDomain(selectedElectiveDomain.value)
        }
        break
      case '채플':
        url = '/lectures/chapel'
        break
      case '교직':
        url = '/lectures/teaching'
        break
      case '연전':
        url = '/lectures/linked-major'
        if (!selectedLinkedMajorTt.value) {
          toast.warning('연계전공을 선택해 주세요.')
          loadingLectures.value = false
          return
        }
        params.ttMajor = selectedLinkedMajorTt.value
        break
      case '융전':
        url = '/lectures/convergence-major'
        if (!selectedIntegratedMajorTt.value) {
          toast.warning('융합전공을 선택해 주세요.')
          loadingLectures.value = false
          return
        }
        params.ttMajor = selectedIntegratedMajorTt.value
        break
      default:
        console.warn('지원하지 않는 카테고리:', searchCategory.value)
        loadingLectures.value = false
        return
    }

    if (searchKeyword.value?.trim()) {
      params.keyword = searchKeyword.value.trim()
    }

    const { data } = await api.get(url, { params })

    const raw = Array.isArray(data) ? data : []
    const grouped = groupLecturesByCourse(raw)

    lectures.value = grouped
    toast.success(`총 ${grouped.length}개의 강의를 불러왔습니다.`)
  } catch (e) {
    console.error('강의 검색 실패:', e)
    lectures.value = []
    toast.error('강의 검색에 실패했습니다.')
  } finally {
    loadingLectures.value = false
  }
}

// 같은 과목(코드/분반)이 시간만 여러 개인 경우 한 항목으로 묶기
function groupLecturesByCourse(rows) {
  const map = new Map()

  for (const row of rows) {
    // key 기준은 과목코드 + 분반(있으면) 조합
    const key = `${row.courseCode || ''}-${row.sectionNo || ''}`

    if (!map.has(key)) {
      // 대표 한 줄 (id, 제목, 교수명, 학점 등은 첫 번째 row 기준으로 사용)
      map.set(key, {
        ...row,
        // 시간/강의실 정보는 slots 배열에 모은다
        slots: [],
      })
    }

    const grouped = map.get(key)
    grouped.slots.push({
      meetingDay: row.meetingDay,
      startTime: row.startTime,
      endTime: row.endTime,
      buildingRoom: row.buildingRoom,
    })
  }

  return Array.from(map.values())
}

/* =========================================
   강의 -> 내 시간표에 추가
   ========================================= */

async function addLectureToTimetable(lec) {
  if (!selectedTimetableId.value) {
    toast.warning('먼저 시간표를 선택해 주세요.')
    return
  }

  addingLecture.value = true
  const timetableId = selectedTimetableId.value

  try {
    await api.post(
      `/user-timetables/${timetableId}/courses`,
      null,
      {
        params: {
          lectureTimetableId: lec.id,
        },
      },
    )

    toast.success('시간표에 강의를 추가했습니다.')
    await loadTimetableDetail(timetableId)
  } catch (e) {
    console.error('시간표에 강의 추가 실패:', e)
    const msg =
      e.response?.data?.message ||
      e.response?.data?.error ||
      '시간표에 강의를 추가하지 못했습니다.'
    toast.error(msg)
  } finally {
    addingLecture.value = false
  }
}

/* =========================================
   초기 로드
   ========================================= */
onMounted(() => {
  if (!isAuthenticated?.value === false) {
    // 비로그인이라도 일단 로드 시도 (백엔드에서 401 처리)
  }
  loadMajors()
  loadIntegratedMajors()
  loadLinkedMajors()
  loadTimetables()
})
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

.tt-pill:hover {
  background: #f9fafb;
}

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
.tt-add-btn:hover {
  border-color: #1f7aec;
  color: #1f7aec;
}

.star-icon {
  font-size: 16px;
  color: #d1d5db;
  cursor: pointer;
  line-height: 1;
}
.star-icon--filled {
  color: #fbbf24;
}

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
.tt-day-label:last-child {
  border-right: none;
}

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
  top: 0;
  bottom: 0;
  width: 20%;
  border-right: 1px solid #f3f4f6;
  pointer-events: none;
}
.tt-col-line:nth-child(1) {
  left: 0;
}
.tt-col-line:nth-child(2) {
  left: 20%;
}
.tt-col-line:nth-child(3) {
  left: 40%;
}
.tt-col-line:nth-child(4) {
  left: 60%;
}
.tt-col-line:nth-child(5) {
  left: 80%;
  border-right: none;
}

.tt-row-line {
  position: absolute;
  left: 0;
  right: 0;
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
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
  z-index: 10;
}

.tt-block__name {
  font-weight: 700;
  color: #3730a3;
  margin-bottom: 2px;
}
.tt-block__info {
  color: #4338ca;
  font-size: 11px;
}

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
.cat-btn:hover {
  background: #f9fafb;
  border-color: #d1d5db;
}
.cat-btn--active {
  background: #1f7aec;
  color: white;
  border-color: #1f7aec;
}

/* 전공 / 교선 / 융전 / 연전 필터 공통 스타일 */
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
}
.filter-select:disabled {
  background: #f3f4f6;
  color: #9ca3af;
  cursor: not-allowed;
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
.search-btn:disabled {
  opacity: 0.7;
  cursor: default;
}
.search-btn:hover:not(:disabled) {
  background: #1f2937;
}

/* 검색 결과 리스트 */
.search-results {
  flex: 1;
  min-height: 300px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  background: #fafafa;
  padding: 10px 12px;
  display: flex;
  flex-direction: column;
}

.empty-msg {
  margin: auto;
  font-size: 14px;
  color: #9ca3af;
  text-align: center;
}

.search-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  height: 100%;
}

.search-list__summary {
  font-size: 13px;
  color: #4b5563;
  margin-bottom: 6px;
}

.search-list__items {
  list-style: none;
  padding: 0;
  margin: 0;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.search-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 8px 10px;
  border-radius: 8px;
  background: #ffffff;
  border: 1px solid #e5e7eb;
}

.search-item__info {
  flex: 1;
  min-width: 0;
}

.search-item__title {
  font-size: 14px;
  font-weight: 600;
  color: #111827;
  margin-bottom: 2px;
}

.search-item__code {
  font-size: 12px;
  color: #6b7280;
  margin-left: 4px;
}

.search-item__meta {
  font-size: 12px;
  color: #4b5563;
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

/* 검색 결과 - 추가 버튼 */
.add-btn {
  flex-shrink: 0;
  padding: 6px 10px;
  border-radius: 6px;
  border: none;
  background: #1f7aec;
  color: #fff;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
}
.add-btn:disabled {
  opacity: 0.6;
  cursor: default;
}
.add-btn:hover:not(:disabled) {
  background: #1d4ed8;
}

/* 기존 패널 스타일 */
.panel {
  width: 100%;
}
.panel__grid {
  display: grid;
  grid-template-columns: minmax(0, 1.2fr) minmax(0, 1fr);
  gap: 16px;
}
.panel__card {
  border-radius: 10px;
  border: 1px solid #eef0f4;
  padding: 14px 16px;
  background: #fafbff;
}
.panel__card--accent {
  background: #f5f3ff;
  border-color: #e0e7ff;
}
.panel__title {
  margin: 0 0 8px;
  font-size: 16px;
  font-weight: 600;
}
.panel__text {
  margin: 0 0 8px;
  font-size: 14px;
  color: #4b5563;
  line-height: 1.6;
}
.panel__list {
  margin: 0 0 8px;
  padding-left: 18px;
  font-size: 13px;
  color: #4b5563;
}
.panel__list li + li {
  margin-top: 2px;
}

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
  .planner__header {
    flex-direction: column;
    align-items: flex-start;
  }
  .planner__subrow {
    flex-direction: column;
    align-items: flex-start;
  }
  .planner__tabs {
    align-self: flex-start;
  }
  .panel__grid {
    grid-template-columns: minmax(0, 1fr);
  }
  .tt-controls {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  .tt-list {
    flex-wrap: wrap;
  }
}
</style>