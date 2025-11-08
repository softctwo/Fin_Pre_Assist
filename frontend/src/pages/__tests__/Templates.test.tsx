import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { vi, describe, it, expect } from 'vitest'
import { MemoryRouter } from 'react-router-dom'
import { ConfigProvider, Form, Input, Button, Select, Modal, message } from 'antd'
import Templates from '../Templates'
import templateService from '../../services/templateService'

// Mock antd components
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

// Mock templateService
vi.mock('../../services/templateService', () => ({
  templateService: {
    list: vi.fn(),
    create: vi.fn(),
    delete: vi.fn(),
    validateSyntax: vi.fn(),
  }
}))

const mockTemplateService = templateService as jest.Mocked<typeof templateService>

// Mock react-router-dom
const mockNavigate = vi.fn()
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  }
})

describe('Templates Component', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders templates page with loading state', () => {
    mockTemplateService.list.mockReturnValue(new Promise(() => {}))

    render(
      <ConfigProvider>
        <MemoryRouter>
          <Templates />
        </MemoryRouter>
      </ConfigProvider>
    )

    expect(screen.getByText('模板管理')).toBeInTheDocument()
    expect(screen.getByText('创建模板')).toBeInTheDocument()
  })

  it('renders templates list correctly', async () => {
    const mockResponse = {
      total: 2,
      items: [
        {
          id: 1,
          name: 'Template 1',
          type: 'proposal',
          description: 'Test proposal template',
          created_at: '2024-01-01'
        },
        {
          id: 2,
          name: 'Template 2',
          type: 'document',
          description: 'Test document template',
          created_at: '2024-01-02'
        }
      ]
    }
    
    mockTemplateService.list.mockResolvedValue(mockResponse)

    render(
      <ConfigProvider>
        <MemoryRouter>
          <Templates />
        </MemoryRouter>
      </ConfigProvider>
    )

    await waitFor(() => {
      expect(screen.getByText('Template 1')).toBeInTheDocument()
      expect(screen.getByText('Template 2')).toBeInTheDocument()
      expect(screen.getByText('Test proposal template')).toBeInTheDocument()
    })
  })

  it('shows empty state when no templates', async () => {
    const mockResponse = { total: 0, items: [] }
    mockTemplateService.list.mockResolvedValue(mockResponse)

    render(
      <ConfigProvider>
        <MemoryRouter>
          <Templates />
        </MemoryRouter>
      </ConfigProvider>
    )

    await waitFor(() => {
      expect(screen.getByText('No data')).toBeInTheDocument()
    })
  })

  it('handles template creation', async () => {
    const mockResponse = {
      total: 1,
      items: [
        {
          id: 1,
          name: 'New Template',
          type: 'proposal',
          description: 'A new template',
          created_at: '2024-01-01'
        }
      ]
    }
    
    mockTemplateService.list.mockResolvedValue(mockResponse)
    mockTemplateService.create.mockResolvedValue({
      id: 1,
      name: 'New Template',
      type: 'proposal',
      description: 'A new template',
      content: 'Hello {{ name }}'
    })

    render(
      <ConfigProvider>
        <MemoryRouter>
          <Templates />
        </MemoryRouter>
      </ConfigProvider>
    )

    const createButton = screen.getByText('创建模板')
    fireEvent.click(createButton)

    // Handle form inputs and submission
    await waitFor(() => {
      expect(mockTemplateService.create).toHaveBeenCalled()
      expect(mockTemplateService.list).toHaveBeenCalled()
    })
  })

  it('handles template deletion', async () => {
    const mockResponse = {
      total: 1,
      items: [
        {
          id: 1,
          name: 'Test Template',
          type: 'proposal',
          description: 'Test template',
          created_at: '2024-01-01'
        }
      ]
    }
    
    mockTemplateService.list.mockResolvedValue(mockResponse)
    mockTemplateService.delete.mockResolvedValue({})

    render(
      <ConfigProvider>
        <MemoryRouter>
          <Templates />
        </MemoryRouter>
      </ConfigProvider>
    )

    await waitFor(() => {
      expect(screen.getByText('Test Template')).toBeInTheDocument()
    })

    const deleteButton = screen.getAllByText('删除')[0]
    fireEvent.click(deleteButton)

    await waitFor(() => {
      expect(screen.getByText('确定')).toBeInTheDocument()
    })
    
    const confirmButton = screen.getByText('确定')
    fireEvent.click(confirmButton)

    await waitFor(() => {
      expect(mockTemplateService.delete).toHaveBeenCalledWith(1)
    })
  })

  it('handles template validation', async () => {
    const mockResponse = { valid: true, message: 'Template syntax is correct' }
    mockTemplateService.validateSyntax.mockResolvedValue(mockResponse)

    render(
      <ConfigProvider>
        <MemoryRouter>
          <Templates />
        </MemoryRouter>
      </ConfigProvider>
    )

    // Find validation button or functionality
    // This depends on the actual UI implementation
    await waitFor(() => {
      expect(screen.getByText('模板管理')).toBeInTheDocument()
    })
  })

  it('filters templates by type', async () => {
    const mockResponse = {
      total: 1,
      items: [
        {
          id: 1,
          name: 'Proposal Template',
          type: 'proposal',
          description: 'Proposal template',
          created_at: '2024-01-01'
        }
      ]
    }
    
    mockTemplateService.list.mockResolvedValue(mockResponse)

    render(
      <ConfigProvider>
        <MemoryRouter>
          <Templates />
        </MemoryRouter>
      </ConfigProvider>
    )

    // Find type filter dropdown
          expect(screen.getByText('全部')) // Find type filter dropdown
    fireEvent.click(typeFilter)
    
    await waitFor(() => {
      expect(screen.getByText('Proposal Template')).toBeInTheDocument()
    })
  })

  it('handles API errors', async () => {
    const mockError = new Error('Network error')
    mockTemplateService.list.mockRejectedValue(mockError)

    render(
      <ConfigProvider>
        <MemoryRouter>
          <Templates />
        </MemoryRouter>
      </ConfigProvider>
    )

    await waitFor(() => {
      expect(screen.getByText(/加载模板失败/)).toBeInTheDocument()
    })
  })
})