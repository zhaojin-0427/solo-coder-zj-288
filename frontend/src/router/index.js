import { createRouter, createWebHashHistory } from 'vue-router'

const routes = [
  { path: '/', redirect: '/tasks' },
  {
    path: '/tasks',
    name: 'Tasks',
    component: () => import('@/views/TaskBoard.vue')
  },
  {
    path: '/orders',
    name: 'Orders',
    component: () => import('@/views/OrderList.vue')
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
  },
  {
    path: '/production',
    name: 'Production',
    component: () => import('@/views/ProductionSchedule.vue')
  },
  {
    path: '/orders/:id',
    name: 'OrderDetail',
    component: () => import('@/views/OrderDetail.vue')
  },
  {
    path: '/budget',
    name: 'Budget',
    component: () => import('@/views/Budget.vue')
  },
  {
    path: '/material',
    name: 'Material',
    component: () => import('@/views/Material.vue')
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

export default router
