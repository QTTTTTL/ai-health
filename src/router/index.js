import { createRouter, createWebHistory } from 'vue-router'
import BackendLayout from '@/components/BackendLayout.vue'
import { iconPropType } from 'element-plus/es/utils/index.mjs'

const backendRoutes = [
  {
    path: '/back',
    component: BackendLayout,
    children: [
      {
        path: 'dashboard',
        component: () => import('@/views/dashboard.vue'),
        meta: { title: '数据分析', icon: 'PieChart' }
         },
         {
          path: 'knowledge',
          component: () => import('@/views/knowledge.vue'),
          meta: { title: '知识文章', icon: 'Message' }

         },
         {
          path: 'emotional',
          component: () => import('@/views/emotional.vue'),
          meta: { title: '情绪日志', icon: 'User' }
         },
         {
          path: 'consultation',
          component: () => import('@/views/consultation.vue'),
          meta: { title: '咨询记录', icon: 'ChatLineSquare' }
         }
      
    ]
  }
]
 
const router = createRouter({
  history: createWebHistory(),
  routes: backendRoutes
})

export default router
