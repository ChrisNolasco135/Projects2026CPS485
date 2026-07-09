import { describe, it, expect, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import router from '../index'
import { useAuthStore } from '../../stores/auth'

describe('Router', () => {
  let authStore;

  beforeEach(() => {
    setActivePinia(createPinia())
    authStore = useAuthStore()
  })

  it('redirects to login if route requires auth and not authenticated', async () => {
    authStore.token = null; // not authenticated
    await router.push('/home')
    await router.isReady()
    expect(router.currentRoute.value.path).toBe('/login')
  })

  it('allows access to protected route if authenticated', async () => {
    authStore.token = 'valid-token'; // authenticated
    await router.push('/home')
    await router.isReady()
    expect(router.currentRoute.value.path).toBe('/home')
  })
})
