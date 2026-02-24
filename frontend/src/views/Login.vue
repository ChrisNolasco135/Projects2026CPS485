<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()

const username = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

const submit = async () => {
  error.value = ''
  loading.value = true
  try {
    await auth.login(username.value, password.value)
    // Navigate to the protected home page after login
    router.push('/home')
  } catch (err) {
    error.value = err?.response?.data?.detail || err?.message || 'Login failed'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <main class="login-page">
    <h2>Sign In</h2>
    <form @submit.prevent="submit" class="login-form">
      <label for="username">Username</label>
      <input id="username" v-model="username" autocomplete="username" />

      <label for="password">Password</label>
      <input id="password" type="password" v-model="password" autocomplete="current-password" />

      <button type="submit" :disabled="loading">{{ loading ? 'Signing in...' : 'Sign In' }}</button>

      <p class="error" v-if="error">{{ error }}</p>
    </form>
  </main>
</template>

<style scoped>
.login-page {
  max-width: 420px;
  margin: 3rem auto;
  padding: 1.5rem;
  border: 2px solid var(--color-border, #8cfbff);
  border-radius: 6px;
  background-color: #a0fff7;
}
.login-form {
  display: grid;
  gap: .75rem;
}
label { font-weight: 600; }
input { padding: .5rem; border: 1px solid #000000; border-radius: 4px; }
button { padding: .6rem 1rem; }
.error { color: #b00020; margin-top: .5rem; }
</style>
