// src/router/index.js
// 추후 구현 예정인 전역 가드 예시
// import api from '../utils/api'
// router.beforeEach(async (to) => {
//   if (!to.meta?.requiresAuth) return true
//   try {
//     await api.get('/auth/me') // 세션 유효 확인
//     return true
//   } catch {
//     return { name: 'login', query: { redirect: to.fullPath } }
//   }
// })

import { createRouter, createWebHistory } from 'vue-router'
import Home from '../pages/Home.vue'
import Board from '../pages/Board/index.vue'
import BoardWrite from '../pages/Board/Write.vue'
import BoardDetail from '../pages/Board/Detail.vue'
import Schedule from '../pages/Schedule/index.vue'
import Friends from '../pages/Friends/index.vue'
import Rag from '../pages/Rag/index.vue'

const routes = [
  // 메인
  { path: '/', name: 'home', component: Home },

  // 게시판 목록
  { path: '/board', name: 'board', component: Board },

  // 게시글 작성
  {
    path: '/board/write',
    name: 'boardWrite',
    component: BoardWrite,
    meta: { requiresAuth: true }, // 나중에 beforeEach에서 로그인 체크
  },

  // 게시글 상세 (GET /api/board/posts/{postId} 와 매칭)
  {
    path: '/board/posts/:id',
    name: 'boardDetail',
    component: BoardDetail,
  },

  // 게시글 수정 화면 (Write.vue 재사용)
  {
    path: '/board/posts/:id/edit',
    name: 'boardEdit',
    component: BoardWrite,
    meta: { requiresAuth: true },
  },

  // 시간표 목록
  { path: '/schedule', name: 'schedule', component: Schedule },

  // 친구 목록
  { path: '/friends', name: 'friends', component: Friends },

  // RAG 검색
  { path: '/rag', name: 'rag', component: Rag },

  // 나머지 → 홈으로
  { path: '/:pathMatch(.*)*', redirect: '/' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  // 페이지 이동 시 항상 맨 위로
  scrollBehavior() {
    return { top: 0 }
  },
})

export default router
