import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { vi, describe, it, expect } from 'vitest'
import { MemoryRouter } from 'react-router-dom'
import { ConfigProvider, Table, Button, Modal, Input } from 'antd'
import Documents from '../Documents'
import documentService from '../../services/documentService'

// Mock antd components
vi.mock('antd', async () => {
  const actual = await vi.importActual('antd')
  return {
    ...actual,
    Table: {
      ...actual.Table,
      usePagination: vi.fn(() => ({ total: 0, current: 1, pageSize: 10, onChange: vi.fn() }))
    }
  }
})

// Mock documentService
vi.mock('../../services/documentService', () => ({
  documentService: {
    list: vi.fn(),
    upload: vi.fn(),
    delete: vi.fn(),
  }
}))

const mockDocumentService = documentService as jest.Mocked<typeof documentService>

// Mock react-router-dom
const mockNavigate = vi.fn()
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  }
})

describe('Documents Component', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders documents page with loading state', () => {
    mockDocumentService.list.mockReturnValue(new Promise(() => {}))

    render(
      <ConfigProvider>
        <MemoryRouter>
          <Documents />
        </MemoryRouter>
      </ConfigProvider>
    )

    expect(screen.getByText('文档管理')).toBeInTheDocument()
    expect(screen.getByText('上传文档')).toBeInTheDocument()
  })

  it('renders documents list correctly', async () => {
    const mockResponse = {
      total: 2,
      items: [
        {
          id: 1,
          title: 'Test Document 1',
          file_path: '/path/to/doc1.pdf',
          file_type: 'pdf',
          created_at: '2024-01-01'
        },
        {
          id: 2,
          title: 'Test Document 2',
          file_path: '/path/to/doc2.docx',
          file_type: 'docx',
          created_at: '2024-01-02'
        }
      ]
    }
    
    mockDocumentService.list.mockResolvedValue(mockResponse)

    render(
      <ConfigProvider>
        <MemoryRouter>
          <Documents />
        </MemoryRouter>
      </ConfigProvider>
    )

    await waitFor(() => {
      expect(screen.getByText('Test Document 1')).toBeInTheDocument()
      expect(screen.getByText('Test Document 2')).toBeInTheDocument()
    })
  })

  it('shows empty state when no documents', async () => {
    const mockResponse = { total: 0, items: [] }
    mockDocumentService.list.mockResolvedValue(mockResponse)

    render(
      <ConfigProvider>
        <MemoryRouter>
          <Documents />
        </MemoryRouter>
      </ConfigProvider>
    )

    await waitFor(() => {
      expect(screen.getByText('No data')).toBeInTheDocument()
    })
  })

  it('handles document upload', async () => {
    const mockResponse = {
      total: 1,
      items: [
        {
          id: 1,
          title: 'Uploaded Document',
          file_path: '/path/to/uploaded.pdf',
          file_type: 'pdf',
          created_at: '2024-01-01'
        }
      ]
    }
    
    mockDocumentService.list.mockResolvedValue(mockResponse)
    mockDocumentService.upload.mockResolvedValue({
      id: 1,
      title: 'test.pdf',
      file_path: '/path/to/test.pdf',
      file_type: 'pdf'
    })

    render(
      <ConfigProvider>
        <MemoryRouter>
          <Documents />
        </MemoryRouter>
      </ConfigProvider>
    )

    const uploadButton = screen.getByText('上传文档')
    fireEvent.click(uploadButton)

    await waitFor(() => {
      expect(mockDocumentService.upload).toHaveBeenCalled()
      expect(mockDocumentService.list).toHaveBeenCalled()
    })
  })

  it('handles document deletion', async () => {
    const mockResponse = {
      total: 1,
      items: [
        {
          id: 1,
          title: 'Test Document',
          file_path: '/path/to/document.pdf',
          file_type: 'pdf',
          created_at: '2024-01-01'
        }
      ]
    }
    
    mockDocumentService.list.mockResolvedValue(mockResponse)
    mockDocumentService.delete.mockResolvedValue({})

    render(
      <ConfigProvider>
        <MemoryRouter>
          <Documents />
        </MemoryRouter>
      </ConfigProvider>
    )

    await waitFor(() => {
      expect(screen.getByText('Test Document')).toBeInTheDocument()
    })

    const deleteButton = screen.getAllByText('删除')[0]
    fireEvent.click(deleteButton)

    await waitFor(() => {
      expect(screen.getByText('确定')).toBeInTheDocument()
    })
    
    const confirmButton = screen.getByText('确定')
    fireEvent.click(confirmButton)

    await waitFor(() => {
      expect(mockDocumentService.delete).toHaveBeenCalledWith(1)
    })
  })

  it('handles search functionality', async () => {
    const mockResponse = {
      total: 1,
      items: [
        {
          id: 1,
          title: 'Search Result',
          file_path: '/path/to/result.pdf',
          file_type: 'pdf',
          created_at: '2024-01-01'
        }
      ]
    }
    
    mockDocumentService.list.mockResolvedValue(mockResponse)

    render(
      <ConfigProvider>
        <MemoryRouter>
          <Documents />
        </MemoryRouter>
      </ConfigProvider>
    )

    const searchInput = screen.getByPlaceholderText('搜索文档')
    fireEvent.change(searchInput, { target: { value: 'search term' } })

    await waitFor(() => {
      expect(screen.getByText('Search Result')).toBeInTheDocument()
      expect(mockDocumentService.list).toHaveBeenCalledWith(expect.objectContaining({
        search: 'search term'
      }))
    })
  })

  it('handles API errors', async () => {
    const mockError = new Error('Network error')
    mockDocumentService.list.mockRejectedValue(mockError)

    render(
      <ConfigProvider>
        <MemoryRouter>
          <Documents />
        </MemoryRouter>
      </ConfigProvider>
    )

    await waitFor(() => {
      expect(screen.getByText(/加载文档失败/)).toBeInTheDocument()
    })
  })

  it('handles pagination', async () => {
    const mockResponse = {
      total: 25,
      items: Array.from({ length: 10 }, (_, i) => ({
        id: i + 1,
        title: `Document ${i + 1}`,
        file_path: `/path/to/doc${i + 1}.pdf`,
        file_type: 'pdf',
        created_at: '2024-01-01'
      }))
    }
    
    mockDocumentService.list.mockResolvedValue(mockResponse)

    render(
      <ConfigProvider>
        <MemoryRouter>
          <Documents />
        </MemoryRouter>
      </ConfigProvider>
    )

    await waitFor(() => {
      expect(screen.getByText('Document 1')).toBeInTheDocument()
      expect(screen.getByText('Document 10')).toBeInTheDocument()
    })
  })
})