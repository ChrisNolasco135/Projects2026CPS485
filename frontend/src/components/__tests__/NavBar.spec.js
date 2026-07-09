import { mount } from '@vue/test-utils'
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import NavBar from '../NavBar.vue'
import { useAuthStore } from '../../stores/auth'

// Mock router
vi.mock('vue-router', () => ({
  useRouter: () => ({
    push: vi.fn()
  })
}))

describe('NavBar.vue', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('renders login form when not authenticated', () => {
    const wrapper = mount(NavBar, {
      global: {
        stubs: ['RouterLink']
      }
    })
    
    expect(wrapper.find('form').exists()).toBe(true)
    expect(wrapper.find('input[placeholder="username"]').exists()).toBe(true)
    expect(wrapper.find('input[placeholder="password"]').exists()).toBe(true)
    expect(wrapper.find('input[placeholder="email"]').exists()).toBe(false)
  })

  it('toggles register mode', async () => {
    const wrapper = mount(NavBar, {
      global: { stubs: ['RouterLink'] }
    })
    
    await wrapper.findAll('button')[1].trigger('click') // Click Register toggle
    expect(wrapper.find('input[placeholder="email"]').exists()).toBe(true)
  })

  it('shows user and logout button when authenticated', () => {
    const auth = useAuthStore()
    auth.token = 'fake-token'
    auth.user = 'testuser'
    
    const wrapper = mount(NavBar, {
      global: { stubs: ['RouterLink'] }
    })
    
    expect(wrapper.text()).toContain('Welcome testuser')
    expect(wrapper.find('form').exists()).toBe(false)
    expect(wrapper.find('button').text()).toBe('Logout')
  })

  it('calls auth login on form submit', async () => {
    const auth = useAuthStore()
    auth.login = vi.fn().mockResolvedValue()
    
    const wrapper = mount(NavBar, {
      global: { stubs: ['RouterLink'] }
    })
    
    await wrapper.find('input[placeholder="username"]').setValue('testuser')
    await wrapper.find('input[placeholder="password"]').setValue('password')
    await wrapper.find('form').trigger('submit')
    
    expect(auth.login).toHaveBeenCalledWith('testuser', 'password')
  })
})
