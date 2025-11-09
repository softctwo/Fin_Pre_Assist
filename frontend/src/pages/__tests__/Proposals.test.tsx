import React from 'react'
import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import { vi, describe, it, expect, beforeEach } from 'vitest'
import { MemoryRouter } from 'react-router-dom'
import { ConfigProvider, Modal } from 'antd'
import Proposals from '../Proposals'
const mockProposalService = vi.hoisted(() => ({
  list: vi.fn(),
  delete: vi.fn(),
}) as Record<string, ReturnType<typeof vi.fn>>)

vi.mock('../../services/proposalService', () => ({
  proposalService: mockProposalService,
  default: mockProposalService,
}))

const mockNavigate = vi.hoisted(() => vi.fn())

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  }
})

describe('Proposals page', () => {
  const mockData = {
    items: [
      { id: 1, title: '方案A', customer_name: '客户A', customer_industry: '金融', status: 'draft', created_at: '2024-01-01T00:00:00Z' },
      { id: 2, title: '方案B', customer_name: '客户B', customer_industry: '保险', status: 'completed', created_at: '2024-01-02T00:00:00Z' },
    ],
  }

  beforeEach(() => {
    vi.clearAllMocks()
    mockProposalService.list.mockResolvedValue(mockData)
  })

  const renderPage = () =>
    render(
      <ConfigProvider>
        <MemoryRouter>
          <Proposals />
        </MemoryRouter>
      </ConfigProvider>,
    )

  it('renders proposals from API', async () => {
    renderPage()

    await waitFor(() => {
      expect(screen.getByText('方案A')).toBeInTheDocument()
      expect(screen.getByText('客户B')).toBeInTheDocument()
    })
  })

  it('navigates to create page', async () => {
    renderPage()

    await waitFor(() => {
      expect(screen.getByText('创建方案')).toBeInTheDocument()
    })

    fireEvent.click(screen.getByText('创建方案'))
    expect(mockNavigate).toHaveBeenCalledWith('/proposals/create')
  })

  it('handles delete confirmation flow', async () => {
    const confirmSpy = vi.spyOn(Modal, 'confirm').mockImplementation(({ onOk }: any) => {
      onOk?.()
      return { destroy: () => undefined } as any
    })
    mockProposalService.delete.mockResolvedValue({})

    renderPage()

    await waitFor(() => {
      expect(screen.getAllByText('删除')[0]).toBeInTheDocument()
    })

    fireEvent.click(screen.getAllByText('删除')[0])

    await waitFor(() => {
      expect(mockProposalService.delete).toHaveBeenCalledWith(1)
    })

    confirmSpy.mockRestore()
  })
})
