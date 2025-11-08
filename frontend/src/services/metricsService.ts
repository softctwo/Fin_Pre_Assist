import React from "react";
import api from './api'

export interface MetricsSummary {
  documents: number
  proposals: number
  cache_hit_rate: string
  cache_type: string
  cache_keys: number
  ai_provider: string
  ai_calls: number
  ai_tokens: number
  vector_searches: number
}

export const getMetricsSummary = async (): Promise<MetricsSummary> => {
  const { data } = await api.get<MetricsSummary>('/metrics/summary')
  return data
}

const metricsService = {
  async getMetricsSummary() {
    return getMetricsSummary()
  },

  async getSystemMetrics() {
    const response = await api.get('/metrics/system')
    return response.data
  },

  async getUserActivityMetrics() {
    const response = await api.get('/metrics/user-activity')
    return response.data
  },

  async getApiMetrics() {
    const response = await api.get('/metrics/api')
    return response.data
  },
}

export default metricsService

