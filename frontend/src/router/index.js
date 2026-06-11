import { createRouter, createWebHashHistory } from 'vue-router'

const routes = [
  { path: '/', redirect: '/tasks' },
  {
    path: '/tasks',
    name: 'Tasks',
    component: () => import('@/views/TaskBoard.vue')
  },
  {
    path: '/checklist',
    name: 'Checklist',
    component: () => import('@/views/Checklist.vue')
  },
  {
    path: '/timeline',
    name: 'Timeline',
    component: () => import('@/views/Timeline.vue')
  },
  {
    path: '/emergency',
    name: 'Emergency',
    component: () => import('@/views/Emergency.vue')
  },
  {
    path: '/stats',
    name: 'Stats',
    component: () => import('@/views/Stats.vue')
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

export default router
