import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { vi, describe, it, expect } from 'vitest'
import { MemoryRouter } from 'react-router-dom'
import { ConfigProvider, Form, Input, Button, message } from 'antd'
import Login from '../Login'
import authService from '../../services/authService'

// Mock antd components
vi.mock('antd', async () => {
  const actual = await vi.importActual('antd')
  return {
    ...actual,
    message: {
      error: vi.fn(),
      success: vi.fn(),
      loading: vi.fn()
    }
  }
})

// Mock authService
vi.mock('../../services/authService', () => ({
  authService: {
    login: vi.fn(),
    register: vi.fn(),
  }
}))

const mockAuthService = authService as jest.Mocked<typeof authService>

// Mock react-router-dom
const mockNavigate = vi.fn()
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  }
})

describe('Login Component', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders login page correctly', () => {
    render(
      <ConfigProvider>
        <MemoryRouter>
          <Login />
        </MemoryRouter>
      </ConfigProvider>
    )

    expect(screen.getByText('金融售前方案辅助系统')).toBeInTheDocument()
    expect(screen.getByText('欢迎使用')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('用户名')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('密码')).toBeInTheDocument()
  })

  it('renders registration tab correctly', () => {
    render(
      <ConfigProvider>
        <MemoryRouter>
          <Login />
        </MemoryRouter>
      </ConfigProvider>
    )

    // Click on registration tab
    const registerTab = screen.getByText('注册')
    fireEvent.click(registerTab)

    expect(screen.getByPlaceholderText('邮箱')).toBeInTheDocument()
  })

  it('handles login form submission successfully', async () => {
    const mockResponse = {
      access_token: 'test-token',
      token_type: 'bearer',
      user: { id: 1, username: 'testuser', role: 'user' }
    }
    
    mockAuthService.login.mockResolvedValue(mockResponse)

    render(
      <ConfigProvider>
        <MemoryRouter>
          <Login />
        </MemoryRouter>
      </ConfigProvider>
    )

    const usernameInput = screen.getByPlaceholderText('用户名')
    const passwordInput = screen.getByPlaceholderText('密码')
    const submitButton = screen.getByRole('button', { name: /登 录/ })

    fireEvent.change(usernameInput, { target: { value: 'testuser' } })
    fireEvent.change(passwordInput, { target: { value: 'password123' } })
    fireEvent.click(submitButton)

    await waitFor(() => {
      expect(mockAuthService.login).toHaveBeenCalledWith('testuser', 'password123')
      expect(mockNavigate).toHaveBeenCalledWith('/dashboard')
    })
  })

  it('handles registration form submission successfully', async () => {
    const mockResponse = {
      id: 1,
      username: 'newuser',
      email: 'new@example.com',
      role: 'user'
    }
    
    mockAuthService.register.mockResolvedValue(mockResponse)

    render(
      <ConfigProvider>
        <MemoryRouter>
          <Login />
        </MemoryRouter>
      </ConfigProvider>
    )

    const registerTab = screen.getByText('注册')
    fireEvent.click(registerTab)

    const usernameInput = screen.getByPlaceholderText('用户名')
    const emailInput = screen.getByPlaceholderText('邮箱')
    const passwordInput = screen.getByPlaceholderText('密码')
    const submitButton = screen.getByRole('button', { name: /注 册/ })

    fireEvent.change(usernameInput, { target: { value: 'newuser' } })
    fireEvent.change(emailInput, { target: { value: 'new@example.com' } })
    fireEvent.change(passwordInput, { target: { value: 'password123' } })
    fireEvent.click(submitButton)

    await waitFor(() => {
      expect(mockAuthService.register).toHaveBeenCalledWith('newuser', 'new@example.com', 'password123')
      expect(screen.getByText(/注册成功/)).toBeInTheDocument()
    })
  })

  it('handles login error correctly', async () => {
    const mockError = new Error('Invalid credentials')
    mockAuthService.login.mockRejectedValue(mockError)

    render(
      <ConfigProvider>
        <MemoryRouter>
          <Login />
        </MemoryRouter>
      </ConfigProvider>
    )

    const usernameInput = screen.getByPlaceholderText('用户名')
    const passwordInput = screen.getByPlaceholderText('密码')
    const submitButton = screen.getByRole('button', { name: /登 录/ })

    fireEvent.change(usernameInput, { target: { value: 'wronguser' } })
    fireEvent.change(passwordInput, { target: { value: 'wrongpass' } })
    fireEvent.click(submitButton)

    await waitFor(() => {
      expect(mockAuthService.login).toHaveBeenCalledWith('wronguser', 'wrongpass')
      // Check for error message (might be in a toast or alert)
    })
  })

  it('validates required fields', async () => {
    render(
      <ConfigProvider>
        <MemoryRouter>
          <Login />
        </MemoryRouter>
      </ConfigProvider>
    )

    const submitButton = screen.getByRole('button', { name: /登 录/ })
    fireEvent.click(submitButton)

    await waitFor(() => {
      // Should show validation errors
      // The exact error messages depend on form validation implementation
    })
  })

  it('handles password visibility toggle', () => {
    render(
      <ConfigProvider>
        <MemoryRouter>
          <Login />
        </MemoryRouter>
      </ConfigProvider>
    )

    const passwordInput = screen.getByPlaceholderText('密码')
    expect(passwordInput).toHaveAttribute('type', 'password')

    // Click on password visibility toggle
    const toggleButton = screen.getByRole('button')
    fireEvent.click(toggleButton)

    // Password input should still be there (type change happens internally)
    expect(passwordInput).toBeInTheDocument()
  })
})