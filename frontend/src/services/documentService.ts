import api from './api'

export interface Document {
  id: number
  title: string
  type: string
  file_name: string
  file_size?: number
  industry?: string
  customer_name?: string
  tags?: string[]
  is_vectorized: number
  created_at: string
}

export const documentService = {
  async upload(file: File, data: {
    title: string
    doc_type: string
    industry?: string
    customer_name?: string
  }) {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('title', data.title)
    formData.append('doc_type', data.doc_type)
    if (data.industry) formData.append('industry', data.industry)
    if (data.customer_name) formData.append('customer_name', data.customer_name)

    const response = await api.post('/documents/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return response.data
  },

  async list(params?: {
    skip?: number
    limit?: number
    doc_type?: string
    industry?: string
  }) {
    const response = await api.get('/documents/', { params })
    return response.data
  },

  async get(id: number) {
    const response = await api.get(`/documents/${id}`)
    return response.data
  },

  async delete(id: number) {
    await api.delete(`/documents/${id}`)
  },
}
