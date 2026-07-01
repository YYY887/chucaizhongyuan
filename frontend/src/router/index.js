import { createRouter, createWebHistory } from 'vue-router'
import { trackVisit } from '../api/route'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/Home.vue')
  },
  {
    path: '/route/:id',
    name: 'RouteDetail',
    component: () => import('../views/RouteDetail.vue')
  },
  {
    path: '/about',
    name: 'About',
    component: () => import('../views/About.vue')
  },
  {
    path: '/recommend',
    name: 'Recommend',
    component: () => import('../views/Recommend.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.afterEach((to) => {
  trackVisit(to.fullPath).catch(() => {})
})

export default router
