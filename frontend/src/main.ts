import { createApp } from 'vue'
import { createPinia } from 'pinia'
import './style.css'
import AppShell from './AppShell.vue'
import router from './router'

const app = createApp(AppShell)
const pinia = createPinia()

app.use(pinia)
app.use(router)
app.mount('#app')
