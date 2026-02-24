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
    // set default header for subsequent requests
    axios.defaults.headers.common.Authorization = `Bearer ${this.token}`
    const userRes = await axios.get(`${API}/users/me`)
    this.user = userRes.data.username
    // Persist token
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
    // remove axios default header
    delete axios.defaults.headers.common.Authorization
  },

  // Restore token on app start
  initFromLocal() {
    const t = localStorage.getItem('token')
    if (t) {
      this.token = t
      // set default header so subsequent API calls include the token
      axios.defaults.headers.common.Authorization = `Bearer ${t}`
      // try to restore user info from backend; clear token on failure
      axios.get(`${API}/users/me`).then(res => {
        this.user = res.data.username
      }).catch(() => {
        this.user = null
        this.token = null
        localStorage.removeItem('token')
        delete axios.defaults.headers.common.Authorization
      })
    }
  }
}
})
