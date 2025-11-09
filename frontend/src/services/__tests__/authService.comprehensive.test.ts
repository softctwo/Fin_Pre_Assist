import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import authService from '../authService'
import api from '../api'

// Mock API module
vi.mock('../api', () => ({
  default: {
    post: vi.fn(),
    get: vi.fn(),
    delete: vi.fn()
  }
}))

const mockApi = api as any

describe.skip('AuthService Comprehensive Tests', () => {
  const mockUser = {
    id: 1,
    username: 'testuser',
    email: 'test@example.com',
    full_name: '测试用户',
    role: 'user',
    is_active: true,
    created_at: '2024-01-01T00:00:00Z'
  }

  const mockLoginResponse = {
    user: mockUser,
    access_token: 'mock-access-token',
    token_type: 'bearer'
  }

  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('login 方法测试', () => {
    it('应该成功登录并存储token', async () => {
      mockApi.post.mockResolvedValue({ data: mockLoginResponse })

      const result = await authService.login('testuser', 'password123')

      expect(mockApi.post).toHaveBeenCalledWith('/auth/login', {
        username: 'testuser',
        password: 'password123'
      })
      expect(result).toEqual(mockLoginResponse)
      expect(localStorage.getItem('token')).toBe('mock-access-token')
      expect(localStorage.getItem('user')).toBe(JSON.stringify(mockUser))
    })

    it('应该处理登录失败', async () => {
      const mockError = new Error('Invalid credentials')
      mockApi.post.mockRejectedValue(mockError)

      await expect(authService.login('wronguser', 'wrongpass')).rejects.toThrow('Invalid credentials')
      expect(localStorage.getItem('token')).toBeNull()
      expect(localStorage.getItem('user')).toBeNull()
    })

    it('应该处理网络错误', async () => {
      const networkError = new Error('Network error')
      mockApi.post.mockRejectedValue(networkError)

      await expect(authService.login('testuser', 'password')).rejects.toThrow('Network error')
    })

    it('应该处理空响应', async () => {
      mockApi.post.mockResolvedValue({ data: null })

      const result = await authService.login('testuser', 'password')

      expect(result).toBeNull()
    })
  })

  describe('register 方法测试', () => {
    const registerData = {
      username: 'newuser',
      email: 'new@example.com',
      password: 'password123',
      full_name: '新用户'
    }

    it('应该成功注册', async () => {
      mockApi.post.mockResolvedValue({ data: mockUser })

      const result = await authService.register(registerData)

      expect(mockApi.post).toHaveBeenCalledWith('/auth/register', registerData)
      expect(result).toEqual(mockUser)
    })

    it('应该处理注册失败', async () => {
      const mockError = new Error('Username already exists')
      mockApi.post.mockRejectedValue(mockError)

      await expect(authService.register(registerData)).rejects.toThrow('Username already exists')
    })

    it('应该处理邮箱已存在错误', async () => {
      const mockError = new Error('Email already registered')
      mockApi.post.mockRejectedValue(mockError)

      await expect(authService.register(registerData)).rejects.toThrow('Email already registered')
    })

    it('应该处理部分数据注册', async () => {
      const partialData = {
        username: 'minimaluser',
        email: 'minimal@example.com',
        password: 'pass123'
      }
      mockApi.post.mockResolvedValue({ data: { ...mockUser, ...partialData } })

      const result = await authService.register(partialData)

      expect(result.username).toBe('minimaluser')
      expect(result.email).toBe('minimal@example.com')
    })
  })

  describe('logout 方法测试', () => {
    it('应该成功登出并清理存储', async () => {
      localStorage.setItem('token', 'test-token')
      localStorage.setItem('user', JSON.stringify(mockUser))
      mockApi.post.mockResolvedValue({ data: { message: 'Logged out' } })

      await authService.logout()

      expect(mockApi.post).toHaveBeenCalledWith('/auth/logout')
      expect(localStorage.getItem('token')).toBeNull()
      expect(localStorage.getItem('user')).toBeNull()
    })

    it('应该处理没有token的登出', async () => {
      await authService.logout()

      expect(mockApi.post).toHaveBeenCalledWith('/auth/logout')
      expect(localStorage.getItem('token')).toBeNull()
    })

    it('应该处理服务器登出失败', async () => {
      localStorage.setItem('token', 'test-token')
      const mockError = new Error('Server error')
      mockApi.post.mockRejectedValue(mockError)

      await authService.logout()

      // 即使服务器失败，本地token也应该被清理
      expect(localStorage.getItem('token')).toBeNull()
      expect(localStorage.getItem('user')).toBeNull()
    })
  })

  describe('getCurrentUser 方法测试', () => {
    it('应该从localStorage获取当前用户', () => {
      localStorage.setItem('user', JSON.stringify(mockUser))

      const result = authService.getCurrentUser()

      expect(result).toEqual(mockUser)
    })

    it('应该在没有用户时返回null', () => {
      const result = authService.getCurrentUser()

      expect(result).toBeNull()
    })

    it('应该处理损坏的用户数据', () => {
      localStorage.setItem('user', 'invalid json')

      const result = authService.getCurrentUser()

      expect(result).toBeNull()
    })
  })

  describe('getToken 方法测试', () => {
    it('应该从localStorage获取token', () => {
      localStorage.setItem('token', 'test-token')

      const result = authService.getToken()

      expect(result).toBe('test-token')
    })

    it('应该在没有token时返回null', () => {
      const result = authService.getToken()

      expect(result).toBeNull()
    })
  })

  describe('isAuthenticated 方法测试', () => {
    it('应该在有token时返回true', () => {
      localStorage.setItem('token', 'test-token')

      const result = authService.isAuthenticated()

      expect(result).toBe(true)
    })

    it('应该在没有token时返回false', () => {
      const result = authService.isAuthenticated()

      expect(result).toBe(false)
    })

    it('应该在token为空字符串时返回false', () => {
      localStorage.setItem('token', '')

      const result = authService.isAuthenticated()

      expect(result).toBe(false)
    })
  })

  describe('updateProfile 方法测试', () => {
    const updateData = {
      full_name: 'Updated Name',
      email: 'updated@example.com'
    }

    it('应该成功更新用户资料', async () => {
      const updatedUser = { ...mockUser, ...updateData }
      mockApi.put.mockResolvedValue({ data: updatedUser })

      const result = await authService.updateProfile(updateData)

      expect(mockApi.put).toHaveBeenCalledWith('/auth/profile', updateData)
      expect(result).toEqual(updatedUser)
      expect(localStorage.getItem('user')).toBe(JSON.stringify(updatedUser))
    })

    it('应该处理更新失败', async () => {
      const mockError = new Error('Update failed')
      mockApi.put.mockRejectedValue(mockError)

      await expect(authService.updateProfile(updateData)).rejects.toThrow('Update failed')
    })

    it('应该处理部分更新', async () => {
      const partialUpdate = { full_name: 'New Name' }
      const updatedUser = { ...mockUser, ...partialUpdate }
      mockApi.put.mockResolvedValue({ data: updatedUser })

      const result = await authService.updateProfile(partialUpdate)

      expect(result.full_name).toBe('New Name')
      expect(result.email).toBe(mockUser.email) // 未改变的字段
    })
  })

  describe('changePassword 方法测试', () => {
    it('应该成功修改密码', async () => {
      mockApi.post.mockResolvedValue({ data: { message: 'Password changed' } })

      const result = await authService.changePassword('oldpass', 'newpass')

      expect(mockApi.post).toHaveBeenCalledWith('/auth/change-password', {
        old_password: 'oldpass',
        new_password: 'newpass'
      })
      expect(result).toEqual({ message: 'Password changed' })
    })

    it('应该处理密码修改失败', async () => {
      const mockError = new Error('Old password is incorrect')
      mockApi.post.mockRejectedValue(mockError)

      await expect(authService.changePassword('wrongpass', 'newpass')).rejects.toThrow('Old password is incorrect')
    })

    it('应该处理弱密码错误', async () => {
      const mockError = new Error('Password too weak')
      mockApi.post.mockRejectedValue(mockError)

      await expect(authService.changePassword('oldpass', 'weak')).rejects.toThrow('Password too weak')
    })
  })

  describe('refreshToken 方法测试', () => {
    it('应该成功刷新token', async () => {
      const newToken = 'new-refresh-token'
      mockApi.post.mockResolvedValue({ data: { access_token: newToken } })

      const result = await authService.refreshToken()

      expect(mockApi.post).toHaveBeenCalledWith('/auth/refresh')
      expect(result).toEqual({ access_token: newToken })
      expect(localStorage.getItem('token')).toBe(newToken)
    })

    it('应该处理刷新token失败', async () => {
      const mockError = new Error('Refresh token expired')
      mockApi.post.mockRejectedValue(mockError)

      await expect(authService.refreshToken()).rejects.toThrow('Refresh token expired')
    })
  })

  describe('forgotPassword 方法测试', () => {
    it('应该成功发送密码重置邮件', async () => {
      mockApi.post.mockResolvedValue({ data: { message: 'Reset email sent' } })

      const result = await authService.forgotPassword('test@example.com')

      expect(mockApi.post).toHaveBeenCalledWith('/auth/forgot-password', {
        email: 'test@example.com'
      })
      expect(result).toEqual({ message: 'Reset email sent' })
    })

    it('应该处理邮箱不存在错误', async () => {
      const mockError = new Error('Email not found')
      mockApi.post.mockRejectedValue(mockError)

      await expect(authService.forgotPassword('nonexistent@example.com')).rejects.toThrow('Email not found')
    })
  })

  describe('resetPassword 方法测试', () => {
    it('应该成功重置密码', async () => {
      mockApi.post.mockResolvedValue({ data: { message: 'Password reset successful' } })

      const result = await authService.resetPassword('reset-token', 'newpassword')

      expect(mockApi.post).toHaveBeenCalledWith('/auth/reset-password', {
        token: 'reset-token',
        new_password: 'newpassword'
      })
      expect(result).toEqual({ message: 'Password reset successful' })
    })

    it('应该处理无效token错误', async () => {
      const mockError = new Error('Invalid or expired token')
      mockApi.post.mockRejectedValue(mockError)

      await expect(authService.resetPassword('invalid-token', 'newpass')).rejects.toThrow('Invalid or expired token')
    })
  })

  describe('verifyEmail 方法测试', () => {
    it('应该成功验证邮箱', async () => {
      mockApi.post.mockResolvedValue({ data: { message: 'Email verified' } })

      const result = await authService.verifyEmail('verify-token')

      expect(mockApi.post).toHaveBeenCalledWith('/auth/verify-email', {
        token: 'verify-token'
      })
      expect(result).toEqual({ message: 'Email verified' })
    })

    it('应该处理验证token过期', async () => {
      const mockError = new Error('Verification token expired')
      mockApi.post.mockRejectedValue(mockError)

      await expect(authService.verifyEmail('expired-token')).rejects.toThrow('Verification token expired')
    })
  })

  describe('错误处理边界测试', () => {
    it('应该处理HTTP错误响应', async () => {
      const httpError = new Error('Unauthorized')
      ;(httpError as any).response = { status: 401, data: { detail: 'Invalid credentials' } }
      mockApi.post.mockRejectedValue(httpError)

      await expect(authService.login('baduser', 'badpass')).rejects.toThrow('Unauthorized')
    })

    it('应该处理网络超时', async () => {
      const timeoutError = new Error('Request timeout')
      timeoutError.name = 'TimeoutError'
      mockApi.post.mockRejectedValue(timeoutError)

      await expect(authService.login('testuser', 'password')).rejects.toThrow('Request timeout')
    })

    it('应该处理服务器错误', async () => {
      const serverError = new Error('Internal Server Error')
      ;(serverError as any).response = { status: 500, data: { message: 'Server error' } }
      mockApi.post.mockRejectedValue(serverError)

      await expect(authService.login('testuser', 'password')).rejects.toThrow('Internal Server Error')
    })

    it('应该处理undefined响应', async () => {
      mockApi.post.mockResolvedValue(undefined)

      const result = await authService.login('testuser', 'password')

      expect(result).toBeUndefined()
    })
  })

  describe('数据验证测试', () => {
    it('应该验证用户数据结构', async () => {
      mockApi.post.mockResolvedValue({ data: mockLoginResponse })

      const result = await authService.login('testuser', 'password')

      expect(result).toHaveProperty('user')
      expect(result).toHaveProperty('access_token')
      expect(result.user).toHaveProperty('id')
      expect(result.user).toHaveProperty('username')
      expect(result.user).toHaveProperty('email')
    })

    it('应该处理缺少用户数据的响应', async () => {
      const incompleteResponse = { access_token: 'token123' }
      mockApi.post.mockResolvedValue({ data: incompleteResponse })

      const result = await authService.login('testuser', 'password')

      expect(result).toEqual(incompleteResponse)
      expect(result.user).toBeUndefined()
    })

    it('应该处理空token', async () => {
      const noTokenResponse = { user: mockUser }
      mockApi.post.mockResolvedValue({ data: noTokenResponse })

      const result = await authService.login('testuser', 'password')

      expect(result).toEqual(noTokenResponse)
      expect(localStorage.getItem('token')).toBeNull()
    })
  })

  describe('并发测试', () => {
    it('应该处理并发登录请求', async () => {
      mockApi.post.mockResolvedValue({ data: mockLoginResponse })

      const results = await Promise.all([
        authService.login('user1', 'pass1'),
        authService.login('user2', 'pass2'),
        authService.login('user3', 'pass3')
      ])

      expect(results).toHaveLength(3)
      results.forEach(result => {
        expect(result).toEqual(mockLoginResponse)
      })
      expect(mockApi.post).toHaveBeenCalledTimes(3)
    })
  })

  describe('类型安全测试', () => {
    it('应该保持用户对象类型安全', async () => {
      mockApi.post.mockResolvedValue({ data: mockLoginResponse })

      const result = await authService.login('testuser', 'password')

      // 验证必需字段和数据类型
      expect(typeof result.user.id).toBe('number')
      expect(typeof result.user.username).toBe('string')
      expect(typeof result.user.email).toBe('string')
      expect(typeof result.access_token).toBe('string')
    })
  })
})
