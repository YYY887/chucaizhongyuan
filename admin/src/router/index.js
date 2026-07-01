import { createRouter, createWebHistory } from 'vue-router'
import { getToken } from '../api/request'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue')
  },
  {
    path: '/',
    component: () => import('../views/AdminLayout.vue'),
    children: [
      { path: '', redirect: '/dashboard' },
      { path: 'dashboard', name: 'Dashboard', component: () => import('../views/Dashboard.vue') },
      { path: 'banners', name: 'Banners', component: () => import('../views/BannerList.vue') },
      { path: 'site-config', name: 'SiteConfig', component: () => import('../views/SiteConfig.vue') },
      { path: 'routes', name: 'Routes', component: () => import('../views/RouteList.vue') },
      { path: 'points', name: 'Points', component: () => import('../views/PointList.vue') },
      { path: 'about', name: 'AboutConfig', component: () => import('../views/AboutConfig.vue') }
    ]
  }
]

const router = createRouter({
  history: createWebHistory('/admin/'),
  routes
})

router.beforeEach((to) => {
  const token = getToken()
  if (to.path !== '/login' && !token) {
    return '/login'
  }
  if (to.path === '/login' && token) {
    return '/dashboard'
  }
  return true
})

export default router
