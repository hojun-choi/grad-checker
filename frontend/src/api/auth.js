// src/api/auth.js
import { api } from './api'

export const authApi = {
  login: (username, password) =>
    api.post('/auth/login', { username, password }),   // 200: {username, roles}
  me:    () => api.get('/auth/me'),                    // 200 or 401
  logout: () => api.post('/auth/logout'),              // 204
}
