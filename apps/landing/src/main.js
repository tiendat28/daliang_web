import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import { siteRoutes } from './routes'
import './styles/site.css'

const router = createRouter({
  history: createWebHistory(),
  routes: siteRoutes(),
  scrollBehavior(to, from, saved) {
    if (saved) return saved
    if (to.hash) return { el: to.hash, behavior: 'smooth' }
    return { top: 0 }
  },
})

createApp(App).use(router).mount('#app')
