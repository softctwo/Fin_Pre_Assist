import api from './api'

export interface Proposal {
  id: number
  title: string
  customer_name: string
  customer_industry?: string
  requirements: string
  executive_summary?: string
  solution_overview?: string
  technical_details?: string
  implementation_plan?: string
  status: string
  created_at: string
  updated_at: string
}

export interface ProposalCreate {
  title: string
  customer_name: string
  customer_industry?: string
  customer_contact?: string
  requirements: string
  reference_document_ids?: number[]
}

export const proposalService = {
  async create(data: ProposalCreate) {
    const response = await api.post('/proposals/', data)
    return response.data
  },

  async list(params?: {
    skip?: number
    limit?: number
    status_filter?: string
  }) {
    const response = await api.get('/proposals/', { params })
    return response.data
  },

  async get(id: number) {
    const response = await api.get(`/proposals/${id}`)
    return response.data
  },

  async update(id: number, data: ProposalCreate) {
    const response = await api.put(`/proposals/${id}`, data)
    return response.data
  },

  async delete(id: number) {
    await api.delete(`/proposals/${id}`)
  },

  async generate(id: number) {
    const response = await api.post(`/proposals/${id}/generate`)
    return response.data
  },

  async export(id: number, format: string) {
    const response = await api.post(`/proposals/${id}/export`, null, {
      params: { format },
    })
    return response.data
  },
}
