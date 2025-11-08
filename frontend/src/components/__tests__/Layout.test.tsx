import React from 'react'
import { render, screen, fireEvent } from '@testing-library/react'
import { vi, describe, it, expect, beforeEach } from 'vitest'
import { MemoryRouter } from 'react-router-dom'
import Layout from '../Layout'

const mockNavigate = vi.fn()
const mockLogout = vi.fn()
const mockUser = { id: 1, username: 'testuser', role: 'user' }

// Mock hooks
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return {
    ...actual,
    useNavigate: () => mockNavigate,
    useLocation: () => ({ pathname: '/dashboard' })
  }
})

vi.mock('../../store/authStore', () => ({
  useAuthStore: () => ({
    user: mockUser,
    logout: mockLogout
  })
}))

describe('Layout Component', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders layout with navigation menu', () => {
    render(
      <MemoryRouter>
        <Layout />
      </MemoryRouter>
    )

    expect(screen.getByText('金融售前方案辅助系统')).toBeInTheDocument()
    expect(screen.getByText('工作台')).toBeInTheDocument()
    expect(screen.getByText('文档管理')).toBeInTheDocument()
    expect(screen.getByText('方案生成')).toBeInTheDocument()
    expect(screen.getByText('模板管理')).toBeInTheDocument()
    expect(screen.getByText('知识库')).toBeInTheDocument()
  })

  it('handles menu navigation', () => {
    render(
      <MemoryRouter>
        <Layout />
      </MemoryRouter>
    )

    const menuItem = screen.getByText('文档管理')
    fireEvent.click(menuItem)

    expect(mockNavigate).toHaveBeenCalledWith('/documents')
  })

  it('displays user information', () => {
    render(
      <MemoryRouter>
        <Layout />
      </MemoryRouter>
    )

    expect(screen.getByText('testuser')).toBeInTheDocument()
  })

  it('handles user logout', () => {
    render(
      <MemoryRouter>
        <Layout />
      </MemoryRouter>
    )

    // Find and click user menu
    const userMenu = screen.getByText('testuser')
    fireEvent.click(userMenu)
    
    // Click logout button
    const logoutButton = screen.getByText('退出登录')
    fireEvent.click(logoutButton)

    expect(mockLogout).toHaveBeenCalled()
    expect(mockNavigate).toHaveBeenCalledWith('/login')
  })
})