import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import './styles/global.css'

// (이미 설치한) 토스트 전역 등록도 여기서 함께
import Toast from 'vue-toastification'
import 'vue-toastification/dist/index.css'

createApp(App)
  .use(router)
  .use(Toast, { position: 'top-right', timeout: 2500 })
  .mount('#app')
