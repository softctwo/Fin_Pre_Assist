// Mock API module for testing
export const api = {
  get: vi.fn(),
  post: vi.fn(),
  put: vi.fn(),
  delete: vi.fn(),
  defaults: {},
  interceptors: {
    request: { use: vi.fn() },
    response: { use: vi.fn() }
  }
}

// Mock axios instance
import { vi } from 'vitest'
vi.mock('axios', () => ({
  create: () => api
}))

export default api