// 完整的服务Mock配置
import { vi } from 'vitest'

// Mock API
export const mockApi = {
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

// Mock Auth Service
export const mockAuthService = {
  login: vi.fn(),
  register: vi.fn(),
  logout: vi.fn(),
  getCurrentUser: vi.fn(),
  refreshToken: vi.fn(),
  updateProfile: vi.fn()
}

// Mock Document Service
export const mockDocumentService = {
  getDocuments: vi.fn(),
  uploadDocument: vi.fn(),
  getDocument: vi.fn(),
  deleteDocument: vi.fn(),
  updateDocument: vi.fn(),
  extractDocumentText: vi.fn(),
  downloadDocument: vi.fn()
}

// Mock Template Service
export const mockTemplateService = {
  getTemplates: vi.fn(),
  createTemplate: vi.fn(),
  getTemplate: vi.fn(),
  updateTemplate: vi.fn(),
  deleteTemplate: vi.fn(),
  validateTemplate: vi.fn(),
  previewTemplate: vi.fn()
}

// Mock Proposal Service
export const mockProposalService = {
  getProposals: vi.fn(),
  createProposal: vi.fn(),
  getProposal: vi.fn(),
  updateProposal: vi.fn(),
  deleteProposal: vi.fn(),
  exportProposal: vi.fn(),
  generateProposal: vi.fn()
}

// Mock Search Service
export const mockSearchService = {
  searchDocuments: vi.fn(),
  searchProposals: vi.fn(),
  searchKnowledge: vi.fn(),
  getSearchSuggestions: vi.fn()
}

// Mock Metrics Service
export const mockMetricsService = {
  getMetricsSummary: vi.fn(),
  getSystemMetrics: vi.fn(),
  getUserActivityMetrics: vi.fn(),
  getApiMetrics: vi.fn()
}

// Mock Auth Store
export const mockAuthStore = {
  user: null,
  token: null,
  isAuthenticated: false,
  login: vi.fn(),
  logout: vi.fn(),
  updateUser: vi.fn()
}

// 默认返回数据
export const mockUser = {
  id: 1,
  username: 'testuser',
  email: 'test@example.com',
  role: 'user',
  created_at: '2024-01-01T00:00:00Z'
}

export const mockDocuments = [
  {
    id: 1,
    title: '测试文档1',
    content: '测试内容1',
    file_path: '/path/to/file1.pdf',
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z'
  },
  {
    id: 2,
    title: '测试文档2',
    content: '测试内容2',
    file_path: '/path/to/file2.pdf',
    created_at: '2024-01-02T00:00:00Z',
    updated_at: '2024-01-02T00:00:00Z'
  }
]

export const mockTemplates = [
  {
    id: 1,
    name: '测试模板1',
    description: '测试描述1',
    content: '模板内容1',
    variables: {},
    is_active: 1,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z'
  }
]

export const mockProposals = [
  {
    id: 1,
    title: '测试方案1',
    customer_name: '测试客户',
    customer_industry: '测试行业',
    requirements: '测试需求',
    status: 'draft',
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z'
  }
]

export const mockMetrics = {
  total_documents: 10,
  total_templates: 5,
  total_proposals: 8,
  active_users: 3,
  system_health: 'good'
}