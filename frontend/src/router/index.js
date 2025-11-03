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

const routes = [
    { path: '/', name: 'home', component: Home },
    { path: '/:pathMatch(.*)*', redirect: '/' },
]

const router = createRouter({
    history: createWebHistory(),
    routes,
})

export default router
