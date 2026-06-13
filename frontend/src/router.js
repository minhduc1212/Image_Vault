import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from './stores'

const routes = [
  {
    path: '/',
    component: () => import('./views/HomeView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/login',
    component: () => import('./views/AuthView.vue'),
    meta: { guestOnly: true }
  },
  {
    path: '/vault/:id',
    component: () => import('./views/VaultView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/admin',
    component: () => import('./views/AdminView.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  const auth = useAuthStore()
  if (to.meta.requiresAuth && !auth.isLoggedIn) return '/login'
  if (to.meta.guestOnly && auth.isLoggedIn) return '/'
  if (to.meta.requiresAdmin && !auth.currentUser?.is_staff) return '/'
})

export default router
