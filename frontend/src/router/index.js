import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import InputPage from '../views/InputPage.vue'
import LoginView from '../views/Login.vue'
import HomeView from '../views/Home.vue'
import DatabaseView from '../views/DatabaseView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/home'
    },
    {
      path: '/login',
      name: 'Login',
      component: LoginView
    },
    {
      path: '/home',
      name: 'Home',
      component: HomeView,
      meta: { requiresAuth: true }
    },
    {
      path: '/input',
      name: 'InputPage',
      component: InputPage,
      meta: { requiresAuth: true }
    },
    {
      path: '/databases',
      name: 'DatabaseView',
      component: DatabaseView,
      meta: { requiresAuth: true }
    },
  ],
})

router.beforeEach((to, from, next) => {
  const auth = useAuthStore()

  if (to.meta.requiresAuth && !auth.isAuthenticated)
    next('/login')
  else
    next()
})

export default router
