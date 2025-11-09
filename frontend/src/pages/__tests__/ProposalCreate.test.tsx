import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { vi, describe, it, expect, beforeEach } from 'vitest'
import { MemoryRouter } from 'react-router-dom'
import { ConfigProvider } from 'antd'
import ProposalCreate from '../ProposalCreate'

const mockProposalService = vi.hoisted(() => ({
  create: vi.fn(),
  generate: vi.fn(),
  validateRequirements: vi.fn(),
  list: vi.fn(),
  get: vi.fn(),
  delete: vi.fn(),
}) as Record<string, ReturnType<typeof vi.fn>>)

vi.mock('../../services/proposalService', () => ({
  proposalService: mockProposalService,
  default: mockProposalService,
}))

// Mock react-router-dom
const mockNavigate = vi.hoisted(() => vi.fn())
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  }
})

// Mock antd message
vi.mock('antd', async () => {
  const actual = await vi.importActual('antd')
  return {
    ...actual,
    message: {
      success: vi.fn(),
      error: vi.fn(),
      loading: vi.fn(),
    }
  }
})

describe('ProposalCreate Component', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  const findSubmitButton = () => {
    const nodes = screen.getAllByText('创建方案')
    for (const node of nodes) {
      const button = node.tagName === 'BUTTON' ? node : node.closest('button')
      if (button) {
        return button as HTMLButtonElement
      }
    }
    return null
  }

  it('renders proposal creation form correctly', () => {
    render(
      <ConfigProvider>
        <MemoryRouter>
          <ProposalCreate />
        </MemoryRouter>
      </ConfigProvider>
    )

    // Check for main heading (use getAllByText to handle multiple instances)
    const headings = screen.getAllByText('创建方案')
    expect(headings.length).toBeGreaterThan(0)
    
    expect(screen.getByText('方案标题')).toBeInTheDocument()
    expect(screen.getByText('客户名称')).toBeInTheDocument()
    expect(screen.getByText('客户需求')).toBeInTheDocument()
    expect(screen.getByText('客户行业')).toBeInTheDocument()
    expect(screen.getByText('客户联系方式')).toBeInTheDocument()
  })

  it('renders form inputs with correct placeholders', () => {
    render(
      <ConfigProvider>
        <MemoryRouter>
          <ProposalCreate />
        </MemoryRouter>
      </ConfigProvider>
    )

    expect(screen.getByPlaceholderText('请输入方案标题')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('请输入客户名称')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('请详细描述客户需求...')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('请输入客户所属行业')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('请输入客户联系方式')).toBeInTheDocument()
  })

  it('handles form submission successfully', async () => {
    const mockProposal = {
      id: 1,
      title: '测试方案',
      customer_name: '测试客户',
      requirements: '测试需求',
      customer_industry: '金融',
      customer_contact: 'test@example.com',
      status: 'draft',
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z'
    }

    mockProposalService.create.mockResolvedValue(mockProposal)

    render(
      <ConfigProvider>
        <MemoryRouter>
          <ProposalCreate />
        </MemoryRouter>
      </ConfigProvider>
    )

    const titleInput = screen.getByPlaceholderText('请输入方案标题')
    const customerInput = screen.getByPlaceholderText('请输入客户名称')
    const requirementsInput = screen.getByPlaceholderText('请详细描述客户需求...')
    const industryInput = screen.getByPlaceholderText('请输入客户所属行业')
    const contactInput = screen.getByPlaceholderText('请输入客户联系方式')
    
    // Find submit button (use getAllByText to handle multiple instances)
    const submitButton = findSubmitButton()
    expect(submitButton).not.toBeNull()

    fireEvent.change(titleInput, { target: { value: '测试方案' } })
    fireEvent.change(customerInput, { target: { value: '测试客户' } })
    fireEvent.change(requirementsInput, { target: { value: '测试需求' } })
    fireEvent.change(industryInput, { target: { value: '金融' } })
    fireEvent.change(contactInput, { target: { value: 'test@example.com' } })
    
    fireEvent.click(submitButton!)

    await waitFor(() => {
      expect(mockProposalService.create).toHaveBeenCalledWith({
        title: '测试方案',
        customer_name: '测试客户',
        requirements: '测试需求',
        customer_industry: '金融',
        customer_contact: 'test@example.com'
      })
    })
  })

  it('handles API errors during submission', async () => {
    const errorMessage = '创建方案失败'
    mockProposalService.create.mockRejectedValue(new Error(errorMessage))

    render(
      <ConfigProvider>
        <MemoryRouter>
          <ProposalCreate />
        </MemoryRouter>
      </ConfigProvider>
    )

    const titleInput = screen.getByPlaceholderText('请输入方案标题')
    const customerInput = screen.getByPlaceholderText('请输入客户名称')
    const requirementsInput = screen.getByPlaceholderText('请详细描述客户需求...')
    
    const submitButton = findSubmitButton()
    expect(submitButton).not.toBeNull()

    fireEvent.change(titleInput, { target: { value: '测试方案' } })
    fireEvent.change(customerInput, { target: { value: '测试客户' } })
    fireEvent.change(requirementsInput, { target: { value: '测试需求' } })
    
    fireEvent.click(submitButton!)

    await waitFor(() => {
      expect(mockProposalService.create).toHaveBeenCalled()
    })
  })

  it('handles cancel button click', () => {
    render(
      <ConfigProvider>
        <MemoryRouter>
          <ProposalCreate />
        </MemoryRouter>
      </ConfigProvider>
    )

    const cancelButton = screen.getByText('取 消')
    fireEvent.click(cancelButton)

    expect(mockNavigate).toHaveBeenCalledWith('/proposals')
  })

  it('shows loading state during submission', async () => {
    mockProposalService.create.mockImplementation(
      () =>
        new Promise((resolve) =>
          setTimeout(() => resolve({ id: 1 }), 100),
        ),
    )

    render(
      <ConfigProvider>
        <MemoryRouter>
          <ProposalCreate />
        </MemoryRouter>
      </ConfigProvider>
    )

    const titleInput = screen.getByPlaceholderText('请输入方案标题')
    const customerInput = screen.getByPlaceholderText('请输入客户名称')
    const requirementsInput = screen.getByPlaceholderText('请详细描述客户需求...')
    
    const submitButton = findSubmitButton()
    expect(submitButton).not.toBeNull()

    fireEvent.change(titleInput, { target: { value: '测试方案' } })
    fireEvent.change(customerInput, { target: { value: '测试客户' } })
    fireEvent.change(requirementsInput, { target: { value: '测试需求' } })
    
    fireEvent.click(submitButton!)
    await waitFor(() => {
      expect(submitButton?.querySelector('.ant-btn-loading-icon')).not.toBeNull()
    })
  })

  it('validates required fields', async () => {
    render(
      <ConfigProvider>
        <MemoryRouter>
          <ProposalCreate />
        </MemoryRouter>
      </ConfigProvider>
    )

    const submitButton = findSubmitButton()
    expect(submitButton).not.toBeNull()
    
    fireEvent.click(submitButton!)

    await waitFor(() => {
      // Form validation should prevent submission
      expect(mockProposalService.create).not.toHaveBeenCalled()
    })
  })
})
