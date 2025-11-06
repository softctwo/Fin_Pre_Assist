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
    const formData = new FormData()
    formData.append('username', data.username)
    formData.append('password', data.password)
    const response = await api.post('/auth/login', formData)
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
