import { describe, it, expect, vi, beforeEach } from 'vitest'
import authService from '../authService'
import api from '../api'

vi.mock('../api', () => ({
  default: {
    post: vi.fn(),
    get: vi.fn(),
  },
}))

const mockedApi = api as unknown as {
  post: ReturnType<typeof vi.fn>
  get: ReturnType<typeof vi.fn>
}

describe('authService', () => {
  beforeEach(() => {
    mockedApi.post.mockReset()
    mockedApi.get.mockReset()
  })

  it('sends login form data to /auth/login', async () => {
    mockedApi.post.mockResolvedValue({ data: { access_token: 'token', token_type: 'bearer' } })

    const result = await authService.login({ username: 'user', password: 'pass' })

    expect(mockedApi.post).toHaveBeenCalledWith(
      '/auth/login',
      expect.any(FormData),
    )
    expect(result).toEqual({ access_token: 'token', token_type: 'bearer' })
  })

  it('registers new user via /auth/register', async () => {
    const payload = { username: 'new', email: 'a@b.com', password: 'pass' }
    mockedApi.post.mockResolvedValue({ data: { id: 1, ...payload } })

    const result = await authService.register(payload)

    expect(mockedApi.post).toHaveBeenCalledWith('/auth/register', payload)
    expect(result.id).toBe(1)
  })

  it('fetches current user via /auth/me', async () => {
    const user = { id: 1, username: 'foo' }
    mockedApi.get.mockResolvedValue({ data: user })

    const result = await authService.getCurrentUser()

    expect(mockedApi.get).toHaveBeenCalledWith('/auth/me')
    expect(result).toEqual(user)
  })
})
