// Mock document service for testing
import { vi } from 'vitest'

export interface Document {
  id: number
  name: string
  type: string
  size: number
  upload_date: string
  content?: string
}

export const mockDocuments: Document[] = [
  {
    id: 1,
    name: '测试文档.pdf',
    type: 'pdf',
    size: 1024 * 1024,
    upload_date: '2024-01-01T00:00:00Z',
    content: '测试文档内容'
  },
  {
    id: 2,
    name: '模板文件.docx',
    type: 'docx',
    size: 512 * 1024,
    upload_date: '2024-01-02T00:00:00Z'
  }
]

const documentService = {
  list: vi.fn(async () => {
    return { documents: mockDocuments, total: mockDocuments.length }
  }),

  upload: vi.fn(async (file: File) => {
    return {
      id: Date.now(),
      name: file.name,
      type: file.type.split('/')[1],
      size: file.size,
      upload_date: new Date().toISOString()
    }
  }),

  delete: vi.fn(async (id: number) => {
    return { message: '删除成功' }
  }),

  get: vi.fn(async (id: number) => {
    const document = mockDocuments.find(d => d.id === id)
    if (!document) {
      throw new Error('文档不存在')
    }
    return document
  })
}

export default documentService
export type { Document }