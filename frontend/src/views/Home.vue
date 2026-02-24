<script setup>
import { computed } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useRouter } from 'vue-router'

const auth = useAuthStore()
const router = useRouter()

const username = computed(() => auth.user || 'Guest')

function goToInput() {
  router.push('/input')
}

function goToDatabases() {
  router.push('/databases')
}
</script>

<template>
  <main class="home-page">
    <h2>Welcome, {{ username }}</h2>
    <p>This is the Home dashboard. Use the navigation to access other pages.</p>
    <div class="button-group">
      <button @click="goToInput" class="btn-primary">Open Input Page</button>
      <button @click="goToDatabases" class="btn-primary">Database Manager</button>
    </div>
  </main>
</template>

<style scoped>
.home-page { max-width: 800px; margin: 3rem auto; padding: 1rem; }
.button-group { display: flex; gap: 1rem; margin-top: 1rem; flex-wrap: wrap; }
.btn-primary {
  padding: 0.6rem 1rem;
  background-color: #0d6efd;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
}
.btn-primary:hover { background-color: #0b5ed7; }
</style>
