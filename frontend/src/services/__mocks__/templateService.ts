// Mock template service for testing
import { vi } from 'vitest'

export interface Template {
  id: number
  name: string
  type: string
  description: string
  content: string
  is_default: boolean
  created_at: string
  updated_at: string
}

export const mockTemplates: Template[] = [
  {
    id: 1,
    name: '测试模板',
    type: 'technical',
    description: '这是一个测试模板',
    content: '{"sections": [{"title": "背景", "content": "项目背景"}]}',
    is_default: true,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z'
  },
  {
    id: 2,
    name: '业务模板',
    type: 'business',
    description: '业务方案模板',
    content: '{"sections": [{"title": "业务需求", "content": "业务需求分析"}]}',
    is_default: false,
    created_at: '2024-01-02T00:00:00Z',
    updated_at: '2024-01-02T00:00:00Z'
  }
]

const templateService = {
  list: vi.fn(async () => {
    return { items: mockTemplates, total: mockTemplates.length }
  }),

  get: vi.fn(async (id: number) => {
    const template = mockTemplates.find(t => t.id === id)
    if (!template) {
      throw new Error('模板不存在')
    }
    return template
  }),

  create: vi.fn(async (data: Partial<Template>) => {
    const newTemplate = {
      id: Date.now(),
      ...data,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    } as Template
    return newTemplate
  }),

  update: vi.fn(async (id: number, data: Partial<Template>) => {
    const template = mockTemplates.find(t => t.id === id)
    if (!template) {
      throw new Error('模板不存在')
    }
    return { ...template, ...data, updated_at: new Date().toISOString() }
  }),

  delete: vi.fn(async (id: number) => {
    return { message: '删除成功' }
  })
}

export default templateService
export type { Template }