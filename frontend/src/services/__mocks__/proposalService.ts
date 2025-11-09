// Mock proposal service for testing
import { vi } from 'vitest'
import type { Proposal, ProposalCreate } from '../proposalService'

export const mockProposal: Proposal = {
  id: 1,
  title: '测试方案',
  customer_name: '测试客户',
  customer_industry: 'banking',
  requirements: '测试需求描述',
  executive_summary: '执行摘要',
  solution_overview: '解决方案概述',
  technical_details: '技术细节',
  implementation_plan: '实施计划',
  status: 'completed',
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-02T00:00:00Z'
}

export const mockProposals = [
  mockProposal,
  {
    ...mockProposal,
    id: 2,
    title: '另一个测试方案',
    status: 'draft'
  }
]

const proposalService = {
  create: vi.fn(async (data: ProposalCreate) => {
    return { id: Date.now(), ...data, status: 'draft', created_at: new Date().toISOString(), updated_at: new Date().toISOString() }
  }),

  list: vi.fn(async (params?: any) => {
    return { total: mockProposals.length, items: mockProposals }
  }),

  get: vi.fn(async (id: number) => {
    const proposal = mockProposals.find(p => p.id === id)
    if (!proposal) {
      throw new Error('方案不存在')
    }
    return proposal
  }),

  update: vi.fn(async (id: number, data: ProposalCreate) => {
    const proposal = mockProposals.find(p => p.id === id)
    if (!proposal) {
      throw new Error('方案不存在')
    }
    return { ...proposal, ...data, updated_at: new Date().toISOString() }
  }),

  generate: vi.fn(async (id: number) => {
    return { message: '生成已开始' }
  }),

  export: vi.fn(async (id: number, format: string) => {
    return { download_url: `http://example.com/proposal.${format}` }
  }),

  delete: vi.fn(async (id: number) => {
    return { message: '删除成功' }
  })
}

export default proposalService
export type { Proposal, ProposalCreate }