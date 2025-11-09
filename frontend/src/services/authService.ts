import api from './api'

export interface LoginData {
  username: string
  password: string
}

export interface RegisterData {
  username: string
  email: string
  password: string
  full_name?: string
}

export const authService = {
  async login(data: LoginData) {
    // 使用URLSearchParams而不是FormData，以确保正确发送application/x-www-form-urlencoded格式
    const params = new URLSearchParams()
    params.append('username', data.username)
    params.append('password', data.password)
    const response = await api.post('/auth/login', params, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    })
    return response.data
  },

  async register(data: RegisterData) {
    const response = await api.post('/auth/register', data)
    return response.data
  },

  async getCurrentUser() {
    const response = await api.get('/auth/me')
    return response.data
  },
}

export default authService
