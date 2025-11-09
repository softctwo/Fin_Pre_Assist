import React from "react";
import api from './api'

export interface SearchResult {
  id: string
  content: string
  metadata: Record<string, any>
  relevance_score: number
}

export const searchService = {
  async searchDocuments(params: {
    query: string
    limit?: number
    doc_type?: string
    industry?: string
  }) {
    const response = await api.post('/search/documents', null, { params })
    return response.data
  },

  async searchKnowledge(params: {
    query: string
    limit?: number
    category?: string
  }) {
    const response = await api.post('/search/knowledge', null, { params })
    return response.data
  },

  async searchSimilarProposals(params: {
    requirements: string
    limit?: number
  }) {
    const response = await api.post('/search/proposals/similar', null, { params })
    return response.data
  },

  async getStats() {
    const response = await api.get('/search/stats')
    return response.data
  },

  async searchProposals(params: any) {
    return this.searchSimilarProposals(params)
  },

  async getSearchSuggestions(query: string) {
    const response = await api.get('/search/suggestions', { params: { query } })
    return response.data
  },
}

export default searchService
