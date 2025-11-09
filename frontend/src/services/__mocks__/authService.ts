// Mock auth service for testing
import { vi } from 'vitest'

export interface LoginData {
  username: string
  password: string
}

export interface RegisterData {
  username: string
  email: string
  password: string
  full_name: string
}

export interface User {
  id: number
  username: string
  email: string
  full_name: string
  role: string
  is_active: boolean
  created_at: string
}

export const mockUser: User = {
  id: 1,
  username: 'testuser',
  email: 'test@example.com',
  full_name: '测试用户',
  role: 'user',
  is_active: true,
  created_at: '2024-01-01T00:00:00Z'
}

const authService = {
  login: vi.fn(async (data: LoginData) => {
    if (data.username === 'testuser' && data.password === 'test123456') {
      return {
        access_token: 'mock-access-token',
        user: mockUser
      }
    }
    throw new Error('用户名或密码错误')
  }),

  register: vi.fn(async (data: RegisterData) => {
    return {
      ...mockUser,
      id: Date.now(),
      username: data.username,
      email: data.email,
      full_name: data.full_name
    }
  }),

  getCurrentUser: vi.fn(async () => {
    return mockUser
  }),

  refreshToken: vi.fn(async () => {
    return { access_token: 'new-mock-access-token' }
  }),

  logout: vi.fn(async () => {
    return { message: '登出成功' }
  })
}

export default authService
export type { LoginData, RegisterData, User }