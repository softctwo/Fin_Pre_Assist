import React from "react";
import api from './api'

export interface Template {
  id: number
  name: string
  type: string
  description?: string
  content: string
  variables?: Record<string, any>
  is_default: number
  is_active: number
  created_at: string
}

const templateService = {
  async create(data: {
    name: string
    type: string
    description?: string
    content: string
    variables?: Record<string, any>
  }) {
    const response = await api.post('/templates/', data)
    return response.data
  },

  async list(params?: {
    skip?: number
    limit?: number
    template_type?: string
  }) {
    const response = await api.get('/templates/', { params })
    return response.data
  },

  async get(id: number) {
    const response = await api.get(`/templates/${id}`)
    return response.data
  },

  async update(id: number, data: {
    name?: string
    description?: string
    content?: string
    variables?: Record<string, any>
  }) {
    const response = await api.put(`/templates/${id}`, data)
    return response.data
  },

  async delete(id: number) {
    await api.delete(`/templates/${id}`)
  },

  async preview(id: number, sampleData: Record<string, any>) {
    const response = await api.post(`/templates/${id}/preview`, sampleData)
    return response.data
  },

  async getVariables(id: number) {
    const response = await api.get(`/templates/${id}/variables`)
    return response.data
  },

  async validateSyntax(content: string) {
    const response = await api.post('/templates/validate', { content })
    return response.data
  },

  async getTemplates(params?: any) {
    return this.list(params)
  },

  async createTemplate(data: any) {
    return this.create(data)
  },

  async validateTemplate(content: string) {
    return this.validateSyntax(content)
  },

  async getTemplate(id: number) {
    return this.get(id)
  },

  async updateTemplate(id: number, data: any) {
    return this.update(id, data)
  },

  async deleteTemplate(id: number) {
    return this.delete(id)
  },

  async previewTemplate(id: number, sampleData: any) {
    return this.preview(id, sampleData)
  },
}

export default templateService
