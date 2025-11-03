// src/composables/useAuth.js
import { ref } from 'vue'

const user = ref(JSON.parse(localStorage.getItem('gc:user') || 'null'))

function login({ username }) {
  user.value = { username }
  localStorage.setItem('gc:user', JSON.stringify(user.value))
}

function logout() {
  user.value = null
  localStorage.removeItem('gc:user')
}

export function useAuth() {
  return {
    user,
    isAuthenticated: () => !!user.value,
    login,
    logout,
  }
}
