import { createRouter, createWebHistory } from 'vue-router'
import BackendLayout from '@/components/BackendLayout.vue'

const backendRoutes = [
  {
    path: '/back',
    component: BackendLayout,
    children: []
  },
  {
    path: '/',
    redirect: '/back'
  }
]
const router = createRouter({
  history: createWebHistory(),
  routes: backendRoutes
})

export default router
