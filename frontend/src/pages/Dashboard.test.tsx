import React from 'react'
import { render, screen, waitFor, within } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach, beforeAll } from 'vitest'
import { getMetricsSummary } from '../services/metricsService'
import type { MetricsSummary } from '../../services/metricsService'

vi.mock('../services/metricsService', () => ({
  getMetricsSummary: vi.fn(),
}))

const mockGetMetricsSummary = vi.mocked(getMetricsSummary)

vi.mock('antd', () => ({
  Card: ({ title, children }: any) => (
    <div data-testid={title ? `card-${title}` : 'card'}>
      {title && <h3>{title}</h3>}
      {children}
    </div>
  ),
  Row: ({ children }: any) => <div data-testid="row">{children}</div>,
  Col: ({ children }: any) => <div data-testid="col">{children}</div>,
  Statistic: ({ title, value }: any) => (
    <div>
      {title && <span>{title}</span>}
      <strong>{value}</strong>
    </div>
  ),
  Spin: ({ tip }: any) => (
    <div role="status">{tip || 'loading'}</div>
  ),
  Alert: ({ message }: any) => (
    <div role="alert">{message}</div>
  ),
}))

let Dashboard: typeof import('./Dashboard').default

beforeAll(async () => {
  Dashboard = (await import('./Dashboard')).default
})

describe('Dashboard page', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders loading state initially', () => {
    mockGetMetricsSummary.mockImplementation(() => new Promise(() => {}))
    render(<Dashboard />)
    expect(screen.getByRole('status')).toHaveTextContent('加载指标中...')
  })

  it('renders error message when API fails', async () => {
    mockGetMetricsSummary.mockRejectedValue(new Error('network'))

    render(<Dashboard />)

    await waitFor(() => {
      expect(screen.getByRole('alert')).toHaveTextContent('无法获取监控指标，请稍后再试')
    })
  })

  it('renders metrics cards after data loads', async () => {
    const metrics: MetricsSummary = {
      documents: 150,
      proposals: 75,
      cache_hit_rate: '85%',
      cache_type: 'Redis',
      cache_keys: 1200,
      ai_provider: 'OpenAI',
      ai_calls: 42,
      ai_tokens: 1024,
      vector_searches: 18,
    }
    mockGetMetricsSummary.mockResolvedValue(metrics)

    render(<Dashboard />)

    await waitFor(() => {
      expect(screen.getByText('文档总数')).toBeInTheDocument()
      expect(screen.getByText('150')).toBeInTheDocument()
      expect(screen.getByText('75')).toBeInTheDocument()
      expect(screen.getByText('监控概览')).toBeInTheDocument()
      expect(screen.getByText('Prometheus / Grafana')).toBeInTheDocument()
    })
  })

  it('derives completed/in-progress proposals correctly', async () => {
    mockGetMetricsSummary.mockResolvedValue({
      documents: 10,
      proposals: 5,
      cache_hit_rate: '10%',
      cache_type: 'Redis',
      cache_keys: 10,
      ai_provider: 'OpenAI',
      ai_calls: 2,
      ai_tokens: 100,
      vector_searches: 3,
    })

    render(<Dashboard />)

    await waitFor(() => {
      const completedSection = screen.getByText('已完成').closest('div')
      const progressSection = screen.getByText('进行中').closest('div')
      expect(completedSection).not.toBeNull()
      expect(progressSection).not.toBeNull()
      expect(within(completedSection as HTMLElement).getByText('3')).toBeInTheDocument()
      expect(within(progressSection as HTMLElement).getByText('2')).toBeInTheDocument()
    })
  })
})
