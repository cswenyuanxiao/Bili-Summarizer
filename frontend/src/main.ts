import { createApp } from 'vue'
import { createPinia } from 'pinia'
import './style.css'
import AppShell from './AppShell.vue'
import router from './router'
import i18n from './locales'

const app = createApp(AppShell)
const pinia = createPinia()

app.use(pinia)
app.use(router)
app.use(i18n)
app.mount('#app')
