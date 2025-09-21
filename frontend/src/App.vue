<template>
  <main style="max-width:720px;margin:40px auto;font-family:system-ui;">
    <h1>졸업요건 사정표 · 데이터베이스응용 1조</h1>

    <section style="margin:16px 0;">
      <h3>수강기록 업로드(JSON)</h3>
      <p>형식 예) [{"studentNo":"20230001","courseCode":"CS201","grade":"A","term":"2024-1"}]</p>
      <textarea v-model="json" rows="6" style="width:100%;"></textarea>
      <div style="display:flex;gap:8px;margin-top:8px;">
        <button @click="upload">업로드</button>
        <span v-if="uploadMsg">{{ uploadMsg }}</span>
      </div>
    </section>

    <section style="margin:24px 0;">
      <h3>사정 평가</h3>
      <label>학번:
        <input v-model="studentNo" placeholder="20230001"/>
      </label>
      <button @click="evaluate" style="margin-left:8px;">평가 실행</button>
      <pre v-if="result" style="margin-top:12px;">{{ JSON.stringify(result, null, 2) }}</pre>
    </section>
  </main>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { api } from './api'

const json = ref('[{"studentNo":"20230001","courseCode":"CS201","grade":"A","term":"2024-1"}]')
const uploadMsg = ref('')
const studentNo = ref('20230001')
const result = ref<any>(null)

async function upload() {
  try {
    const data = JSON.parse(json.value)
    const res = await api.post('/import/taken', data)
    uploadMsg.value = '업로드 완료: ' + JSON.stringify(res.data)
  } catch (e:any) {
    uploadMsg.value = '업로드 실패: ' + (e.message || e)
  }
}

async function evaluate() {
  const res = await api.post('/evaluate', { studentNo: studentNo.value })
  result.value = res.data
}
</script>
