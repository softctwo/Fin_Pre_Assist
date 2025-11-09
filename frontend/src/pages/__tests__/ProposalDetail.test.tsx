import React from 'react'
import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import { vi, describe, it, expect, beforeEach } from 'vitest'
import { MemoryRouter } from 'react-router-dom'
import { ConfigProvider } from 'antd'
import ProposalDetail from '../ProposalDetail'
const mockProposalService = vi.hoisted(() => ({
  get: vi.fn(),
  export: vi.fn(),
  delete: vi.fn(),
  generate: vi.fn(),
}))

vi.mock('../../services/proposalService', () => ({
  proposalService: mockProposalService,
  default: mockProposalService,
}))

const mockNavigate = vi.hoisted(() => vi.fn())

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return {
    ...actual,
    useParams: () => ({ id: '1' }),
    useNavigate: () => mockNavigate,
  }
})

describe('ProposalDetail', () => {
  const mockProposal = {
    id: 1,
    title: '测试方案',
    customer_name: '测试客户',
    customer_industry: '金融',
    requirements: '测试需求描述',
    status: 'draft',
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-02T00:00:00Z',
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  const renderPage = () =>
    render(
      <ConfigProvider>
        <MemoryRouter>
          <ProposalDetail />
        </MemoryRouter>
      </ConfigProvider>,
    )

  it('renders proposal info when loaded', async () => {
    mockProposalService.get.mockResolvedValue(mockProposal)

    renderPage()

    await waitFor(() => {
      expect(screen.getByText('测试方案')).toBeInTheDocument()
      expect(screen.getByText('测试客户')).toBeInTheDocument()
    })
  })

  it('shows fallback when proposal missing', async () => {
    mockProposalService.get.mockResolvedValue(null)
    renderPage()
    await waitFor(() => {
      expect(screen.getByText('方案不存在')).toBeInTheDocument()
    })
  })

  it('handles generate action', async () => {
    mockProposalService.get.mockResolvedValue(mockProposal)
    mockProposalService.generate.mockResolvedValue({ status: 'generating' })

    renderPage()

    await waitFor(() => {
      expect(screen.getByText('生成方案')).toBeInTheDocument()
    })

    fireEvent.click(screen.getByText('生成方案'))

    await waitFor(() => {
      expect(mockProposalService.generate).toHaveBeenCalledWith(1)
    })
  })

  it('opens export link for completed proposals', async () => {
    mockProposalService.get.mockResolvedValue({ ...mockProposal, status: 'completed' })
    const openSpy = vi.spyOn(window, 'open').mockImplementation(() => null)

    renderPage()

    await waitFor(() => {
      expect(screen.getByText('导出Word')).toBeInTheDocument()
    })

    fireEvent.click(screen.getByText('导出Word'))

    await waitFor(() => {
      expect(openSpy).toHaveBeenCalledWith('/api/v1/proposals/1/export?format=docx', '_blank')
    })

    openSpy.mockRestore()
  })

  it('navigates back to proposals list', async () => {
    mockProposalService.get.mockResolvedValue(mockProposal)

    renderPage()

    const backButton = await screen.findByRole('button', { name: /返\s*回/ })
    fireEvent.click(backButton)
    expect(mockNavigate).toHaveBeenCalledWith('/proposals')
  })
})
