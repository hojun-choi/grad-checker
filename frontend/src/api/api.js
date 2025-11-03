// src/api/api.js
import axios from 'axios'

export const api = axios.create({
  baseURL: '/api',
  withCredentials: true,      // ✅ 세션 쿠키 보내기
  timeout: 10000,
})

function getCookie(name) {
  const m = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)')
  return m ? decodeURIComponent(m.pop()) : ''
}

api.interceptors.request.use((config) => {
  // ✅ CSRF 헤더 동기화 (POST/PUT/PATCH/DELETE 시)
  const token = getCookie('XSRF-TOKEN')
  if (token && /^(post|put|patch|delete)$/i.test(config.method)) {
    config.headers['X-XSRF-TOKEN'] = token
  }
  return config
})
