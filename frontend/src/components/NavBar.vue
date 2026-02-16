<script setup>
import { ref } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useRouter } from 'vue-router'

const auth = useAuthStore()
const router = useRouter()

const username = ref('')
const password = ref('')
const email = ref('')
const isRegister = ref(false)

function submitLogin() {
  auth.login(username.value, password.value)
  clear()
}

function submitRegister() {
  auth.register(email.value, username.value, password.value)
  clear()
  isRegister.value = false
}

/*
async function submitRegister() {
  try {
    await auth.register(email.value, username.value, password.value)
    clear()
    isRegister.value = false
  } catch (e) {
    alert(e.message)
  }
}
*/

function clear() {
  username.value = ''
  password.value = ''
  email.value = ''
}

function logout() {
  auth.logout()
  router.push('/input')
}
</script>

<template>
  <nav class="navbar navbar-dark bg-dark fixed-top px-3">

    <RouterLink class="navbar-brand" to="/input">
      Smart DB
    </RouterLink>

    <div class="ms-auto d-flex align-items-center">

      <!-- NOT LOGGED IN -->
      <form
        v-if="!auth.isAuthenticated"
        class="d-flex gap-2 align-items-center"
        @submit.prevent="isRegister ? submitRegister() : submitLogin()"
      >
        <!-- Email only for register -->
        <input
          v-if="isRegister"
          class="form-control form-control-sm"
          type="email"
          placeholder="email"
          v-model="email"
          required
        />

        <input
          class="form-control form-control-sm"
          placeholder="username"
          v-model="username"
          required
        />

        <input
          class="form-control form-control-sm"
          type="password"
          placeholder="password"
          v-model="password"
          required
        />

        <button class="btn btn-success btn-sm">
          {{ isRegister ? 'Register' : 'Login' }}
        </button>

        <button
          type="button"
          class="btn btn-outline-info btn-sm"
          @click="isRegister = !isRegister"
        >
          {{ isRegister ? 'Cancel' : 'Register' }}
        </button>
      </form>

      <!-- LOGGED IN -->
      <div v-else class="d-flex align-items-center gap-3 text-white">
        <span>Welcome {{ auth.user }}</span>
        <button class="btn btn-outline-light btn-sm" @click="logout">
          Logout
        </button>
      </div>

    </div>
  </nav>
</template>
