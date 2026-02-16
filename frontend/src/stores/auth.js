import { defineStore } from 'pinia'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: null
  }),

  getters: {
    isAuthenticated: (state) => !!state.token
  },

  actions: {
    async login(username, password) {
      if (username && password) {
        this.user = username
        this.token = 'demo-token'
      }
    },

    /*
    async login(username, password) {
    const res = await fetch('http://localhost:8000/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
    })

    if (!res.ok) throw new Error('Invalid credentials')

    const data = await res.json()
    this.user = data.username
    this.token = data.token
    }
    */

    async register(email, username, password) {
      if (email && username && password) {
        this.user = username
        this.token = 'demo-token'
      }
    },


    /*
    async register(email, username, password) {
    const res = await fetch('http://localhost:8000/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      email,
      username,
      password
    })
    })

    if (!res.ok) {
      const err = await res.json()
      throw new Error(err.message || 'Registration failed')
    }

    const data = await res.json()

    this.user = data.username
    this.token = data.token
    }
    */

    logout() {
      this.user = null
      this.token = null
    }
  }
})
