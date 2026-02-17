import { defineStore } from 'pinia'
import axios from 'axios'

const API = 'http://localhost:8000'

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
    const params = new URLSearchParams()
    params.append('username', username)
    params.append('password', password)
    const res = await axios.post(`${API}/login`, params, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    })
    this.token = res.data.access_token
    // Optionally fetch user info:
    const userRes = await axios.get(`${API}/users/me`, {
      headers: { Authorization: `Bearer ${this.token}` }
    })
    this.user = userRes.data.username
    // Persist token if desired:
    localStorage.setItem('token', this.token)
  },

  async register(email, username, password) {
    const res = await axios.post(`${API}/register`, {
      email, username, password
    })
  },

  logout() {
    this.user = null
    this.token = null
    localStorage.removeItem('token')
  },

  // Restore token on app start
  initFromLocal() {
    const t = localStorage.getItem('token')
    if (t) this.token = t
  }
}
})
