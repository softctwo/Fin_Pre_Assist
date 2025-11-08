import React from "react";
import { render, screen, waitFor } from '@testing-library/react'
import { vi, describe, it, expect } from 'vitest'

import Dashboard from '../Dashboard'
import { getMetricsSummary } from '../../services/metricsService'

vi.mock('../../services/metricsService', () => ({
  getMetricsSummary: vi.fn(),
}))

const mockedGetMetricsSummary = vi.mocked(getMetricsSummary)

describe('Dashboard metrics summary', () => {
  it('displays metrics data when API succeeds', async () => {
    mockedGetMetricsSummary.mockResolvedValue({
      documents: 10,
      proposals: 5,
      cache_hit_rate: '80.00%',
      cache_type: 'memory',
      cache_keys: 2,
      ai_provider: 'openai',
      ai_calls: 3,
      ai_tokens: 1200,
      vector_searches: 15,
    })

    render(<Dashboard />)

    await waitFor(() => {
      expect(screen.getByText('文档总数')).toBeInTheDocument()
      expect(screen.getByText('10')).toBeInTheDocument()
      expect(screen.getByText(/缓存命中率/)).toBeInTheDocument()
      expect(screen.getByText('向量搜索次数')).toBeInTheDocument()
  })
  })

  it('shows error alert when API fails', async () => {
    mockedGetMetricsSummary.mockRejectedValueOnce(new Error('network'))

    render(<Dashboard />)

    await waitFor(() => {
      expect(screen.getByText(/无法获取监控指标/)).toBeInTheDocument()
    })
  })
})
