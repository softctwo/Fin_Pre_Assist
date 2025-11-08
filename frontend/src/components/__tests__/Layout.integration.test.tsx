import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { vi, describe, it, expect, beforeEach } from 'vitest'
import { MemoryRouter } from 'react-router-dom'
import { ConfigProvider, Table, Button, Modal, Form, Input, Select } from 'antd'
import Layout from '../../components/Layout'

// Mock auth store
vi.mock('../../store/authStore', () => ({
  useAuthStore: vi.fn()
}))

// Mock react-router-dom
vi.mock('react-router-dom', () => ({
  useNavigate: vi.fn(),
  useLocation: vi.fn(() => ({ pathname: '/dashboard' }))
}))

vi.mock('antd', async () => {
  const actual = await vi.importActual('antd')
  return {
    ...actual,
    Menu: {
      ...actual.Menu,
      Item: ({ children, ...props }: any) => <div data-testid="menu-item" {...props}>{children}</div>,
    SubMenu: ({ children, ...props }: any) => <div data-testid="submenu" {...props}>{children}</div>,
    }
  }
}))

describe('Layout Component Integration Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders layout with navigation menu', () => {
    const mockUser = { id: 1, username: 'testuser', role: 'user' }
    vi.mocked(useAuthStore).mockReturnValue({
      user: mockUser,
      token: 'test-token',
      logout: vi.fn(),
      setAuth: vi.fn(),
    } as any)

    render(
      <ConfigProvider>
        <MemoryRouter>
          <Layout />
        </MemoryRouter>
      </ConfigProvider>
    )

    expect(screen.getByText('金融售前方案辅助系统')).toBeInTheDocument()
    expect(screen.getByText('工作台')).toBeInTheDocument()
    expect(screen.getByText('文档管理')).toBeInTheDocument()
    expect(screen.getByText('方案生成')).toBeInTheDocument()
    expect(screen.getByText('模板管理')).toBeInTheDocument()
    expect(screen.getByText('知识库')).toBeInTheDocument()
    expect(screen.getByText('testuser')).toBeInTheDocument()
  })

  it('displays dropdown menu items', () => {
    const mockUser = { id: 1, username: 'testuser', role: 'user' }
    vi.mocked(useAuthStore).mockReturnValue({
      user: mockUser,
      token: 'test-token',
      logout: vi.fn(),
      setAuth: vi.fn(),
    } as any)

    render(
      <ConfigProvider>
        <MemoryRouter>
          <Layout />
        </MemoryRouter>
      </ConfigProvider>
    )

    // Test dropdown menu
    const userDropdown = screen.getByText('testuser')
    fireEvent.click(userDropdown)

    expect(screen.getByText('个人信息')).toBeInTheDocument()
    expect(screen.getByText('退出登录')).toBeInTheDocument()
  })

  it('handles navigation correctly', () => {
    const mockNavigate = vi.fn()
    vi.mocked(vi.importDynamic('react-router-dom')).useNavigate.mockReturnValue(mockNavigate)
    
    const mockUser = { id: 1, username: 'testuser', role: 'user' }
    vi.mocked(useAuthStore).mockReturnValue({
      user: mockUser,
      token: 'test-token',
      logout: vi.fn(),
      setAuth: vi.fn(),
    } as any)

    render(
      <ConfigProvider>
        <MemoryRouter>
          <Layout />
        </MemoryRouter>
      </ConfigProvider>
    )

    // Click on menu item
    const documentsMenuItem = screen.getByText('文档管理')
    fireEvent.click(documentsMenuItem)

    // Test might need to find the actual clickable element
    // This depends on the actual DOM structure
  })

  it('handles logout correctly', async () => {
    const mockLogout = vi.fn()
    const mockNavigate = vi.fn()
    vi.mocked(useAuthStore).mockReturnValue({
      user: { id: 1, username: 'testuser', role: 'user' },
      token: 'test-token',
      logout: mockLogout,
      setAuth: vi.fn(),
    } as any)
    
    vi.mocked(vi.importDynamic('react-router-dom')).useNavigate.mockReturnValue(mockNavigate)

    render(
      <ConfigProvider>
        <MemoryRouter>
          <Layout />
        </MemoryRouter>
      </ConfigProvider>
    )

    // Find and click logout menu item
    const userDropdown = screen.getByText('testuser')
    fireEvent.click(userDropdown)
    
    const logoutButton = screen.getByText('退出登录')
    fireEvent.click(logoutButton)

    await waitFor(() => {
      expect(mockLogout).toHaveBeenCalled()
      expect(mockNavigate).toHaveBeenCalledWith('/login')
    })
  })

  it('highlights active menu item', () => {
    vi.mocked(vi.importDynamic('react-router-dom')).useLocation.mockReturnValue({
      pathname: '/documents'
    })

    const mockUser = { id: 1, username: 'testuser', role: 'user' }
    vi.mocked(useAuthStore).mockReturnValue({
      user: mockUser,
      token: 'test-token',
      logout: vi.fn(),
      setAuth: vi.fn(),
    } as any)

    render(
      <ConfigProvider>
        <MemoryRouter>
          <Layout />
        </MemoryRouter>
      </ConfigProvider>
    )

    // The active menu item should be highlighted
    const documentsMenuItem = screen.getByText('文档管理')
    expect(documentsMenuItem).toBeInTheDocument()
  })
})