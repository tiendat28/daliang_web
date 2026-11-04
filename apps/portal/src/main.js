import { createApp } from 'vue'
import App from '@/App.vue'
import router from '@/router/index'
import '@/core/style.css'

// Doi router xac dinh xong trang dau (kiem tra dang nhap) roi moi ve, khoi nhay khung admin
const app = createApp(App).use(router)
router.isReady().then(() => app.mount('#app'))
