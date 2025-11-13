// 추후 구현
// src/router/index.js (요지)
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

const routes = [
    { path: '/', name: 'home', component: Home },
    { path: '/:pathMatch(.*)*', redirect: '/' },
    { path: '/board', name: 'board', component: Board },
    { path: '/board/write', name: 'boardWrite', component: BoardWrite },
]

const router = createRouter({
    history: createWebHistory(),
    routes,
})

export default router
