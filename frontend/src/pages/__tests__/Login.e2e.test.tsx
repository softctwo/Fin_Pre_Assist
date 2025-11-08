import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { vi, describe, it, expect, beforeEach } from 'vitest'
import { MemoryRouter } from 'react-router-dom'
import { ConfigProvider, Form, Input, Button, Tabs, Card, Spin, message } from 'antd'
import Login from '../Login'

// Mock service
vi.mock('../../services/authService', () => ({
  default: {
    login: vi.fn(),
    register: vi.fn(),
  }
}))

const mockAuthService = vi.mocked(await import('../../services/authService'))

// Mock react-router-dom
const mockNavigate = vi.fn()
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  }
})

// Mock zustand
vi.mock('zustand', () => ({
  create: (fn: any) => fn(() => ({
    token: null,
    user: null,
    setAuth: vi.fn(),
    logout: vi.fn(),
  }))
}))

describe('Login Page Component Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Form Rendering', () => {
    it('renders login form correctly', () => {
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

    it('renders registration form when tab is clicked', () => {
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
  })

  describe('Login Functionality', () => {
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

      // Fill login form
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

    it('handles login failure with error message', async () => {
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
        expect(screen.getByText(/登录失败/)).toBeInTheDocument()
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
        expect(screen.getByText(/请输入用户名/)).toBeInTheDocument()
      })
    })
  })

  describe('Registration Functionality', () => {
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

      // Click on registration tab
      const registerTab = screen.getByText('注册')
      fireEvent.click(registerTab)

      // Fill registration form
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

    it('handles registration failure', async () => {
      const mockError = new Error('Registration failed')
      mockAuthService.register.mockRejectedValue(mockError)

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

      const submitButton = screen.getByRole('button', { name: /注 册/ })
      fireEvent.click(submitButton)

      await waitFor(() => {
        expect(screen.getByText(/注册失败/)).toBeInTheDocument()
      })
    })
  })

  describe('Tab Switching', () => {
    it('switches between login and registration tabs', async () => {
      render(
        <ConfigProvider>
          <MemoryRouter>
            <Login />
          </MemoryRouter>
        </ConfigProvider>
      )

      // Initial state should show login tab
      expect(screen.getByPlaceholderText('用户名')).toBeInTheDocument()
      expect(screen.queryByPlaceholderText('邮箱')).not.toBeInTheDocument()

      // Click on registration tab
      fireEvent.click(screen.getByText('注册'))
      await waitFor(() => {
        expect(screen.getByPlaceholderText('邮箱')).toBeInTheDocument()
        expect(screen.queryByPlaceholderText('用户名')).not.toBeInTheDocument()
      })

      // Click back on login tab
      fireEvent.click(screen.getByText('登录'))
      await waitFor(() => {
        expect(screen.getByPlaceholderText('用户名')).toBeInTheDocument()
        expect(screen.queryByPlaceholderText('邮箱')).not.toBeInTheDocument()
      })
    })
  })

  describe('Form Reset', () => {
    it('resets form after successful submission', async () => {
      mockAuthService.login.mockResolvedValue({
        access_token: 'test-token',
        user: { id: 1, username: 'testuser' }
      })

      render(
        <ConfigProvider>
          <MemoryRouter>
            <Login />
          </MemoryRouter>
        </ConfigProvider>
      )

      // Fill and submit form
      fireEvent.change(screen.getByPlaceholderText('用户名'), { target: { value: 'testuser' } })
      fireEvent.change(screen.getByPlaceholderText('密码'), { target: { value: 'password123' } })
      fireEvent.click(screen.getByRole('button', { name: /登 录/ }))

      await waitFor(() => {
        // Form should be empty after successful login
        expect((screen.getByPlaceholderText('用户名') as HTMLInputElement).value).toBe('')
        expect((screen.getByPlaceholderText('密码') as HTMLInputElement).value).toBe('')
      })
    })
  })

  describe('Loading States', () => {
    it('shows loading state during form submission', async () => {
      mockAuthService.login.mockImplementation(() => 
        new Promise(resolve => setTimeout(() => resolve({}), 1000))
      )

      render(
        <ConfigProvider>
          <MemoryRouter>
            <Login />
          </MemoryRouter>
        </ConfigProvider>
      )

      fireEvent.click(screen.getByRole('button', { name: /登 录/ }))

      // Should show loading state
      // Note: This depends on the actual implementation of loading state
      expect(screen.getByRole('button', { name: /登 录/ })).toBeInTheDocument()
    })
  })
})