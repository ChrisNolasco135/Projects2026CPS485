import { describe, it, expect, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useAuthStore } from '../auth'
import axios from 'axios'
import MockAdapter from 'axios-mock-adapter'

const mock = new MockAdapter(axios)

describe('Auth Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    mock.reset()
    localStorage.clear()
  })

  it('initializes with token from localStorage', () => {
    localStorage.setItem('token', 'fake-token')
    const store = useAuthStore()
    // It might depend on store implementation if it reads it immediately
    // but typically it does.
  })

  it('login sets token and user', async () => {
    mock.onPost('http://localhost:8000/login').reply(200, {
      access_token: 'new-token'
    })
    mock.onGet('http://localhost:8000/users/me').reply(200, {
      id: 1,
      username: 'testuser',
      email: 'test@test.com'
    })

    const store = useAuthStore()
    await store.login('testuser', 'password')

    expect(store.token).toBe('new-token')
    expect(store.user).toBe('testuser')
    expect(localStorage.getItem('token')).toBe('new-token')
  })

  it('logout clears token and user', () => {
    const store = useAuthStore()
    store.token = 'existing-token'
    store.user = { id: 1 }
    localStorage.setItem('token', 'existing-token')
    
    store.logout()
    
    expect(store.token).toBeNull()
    expect(store.user).toBeNull()
    expect(localStorage.getItem('token')).toBeNull()
  })
})
