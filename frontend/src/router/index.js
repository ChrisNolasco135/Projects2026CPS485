import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/InputPage.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/InputPage',
      name: 'InputPage',
      component: HomeView,
    },
  ],
})

export default router
