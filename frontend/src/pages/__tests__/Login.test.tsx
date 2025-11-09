import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { vi, describe, it, expect } from 'vitest'
import { MemoryRouter } from 'react-router-dom'
import { ConfigProvider } from 'antd'
import Login from '../Login'
const mockAuthService = vi.hoisted(() => ({
  login: vi.fn(),
  register: vi.fn(),
  getCurrentUser: vi.fn(),
}))

vi.mock('../../services/authService', () => ({
  authService: mockAuthService,
  default: mockAuthService,
}))

const setAuthMock = vi.hoisted(() => vi.fn())

vi.mock('../../store/authStore', () => ({
  useAuthStore: () => ({
    setAuth: setAuthMock,
  }),
}))

const mockNavigate = vi.hoisted(() => vi.fn())

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  }
})

vi.mock('antd', async () => {
  const actual = await vi.importActual('antd')
  return {
    ...actual,
    message: {
      success: vi.fn(),
      error: vi.fn(),
    },
  }
})

const renderLogin = () =>
  render(
    <ConfigProvider>
      <MemoryRouter>
        <Login />
      </MemoryRouter>
    </ConfigProvider>,
  )

const findButtonByText = (text: string) => {
  const pattern = new RegExp(text.split('').join('\\s*'))
  return screen.getByRole('button', { name: pattern }) as HTMLButtonElement
}

describe('Login page', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('submits login form and sets auth state', async () => {
    mockAuthService.login.mockResolvedValue({ access_token: 'token' })
    mockAuthService.getCurrentUser.mockResolvedValue({ id: 1, username: 'tester' })

    renderLogin()

    fireEvent.change(screen.getByPlaceholderText('用户名'), { target: { value: 'tester' } })
    fireEvent.change(screen.getByPlaceholderText('密码'), { target: { value: 'secret' } })
    fireEvent.click(findButtonByText('登录'))

    await waitFor(() => {
      expect(mockAuthService.login).toHaveBeenCalled()
      expect(setAuthMock).toHaveBeenCalledWith('token', { id: 1, username: 'tester' })
      expect(mockNavigate).toHaveBeenCalledWith('/')
    })
  })

  it('submits registration form and flips to login tab', async () => {
    mockAuthService.register.mockResolvedValue({ id: 1 })
    renderLogin()

    fireEvent.click(screen.getByText('注册'))
    const usernameFields = screen.getAllByPlaceholderText('用户名')
    fireEvent.change(usernameFields[1], { target: { value: 'newuser' } })
    fireEvent.change(screen.getByPlaceholderText('邮箱'), { target: { value: 'a@b.com' } })
    const passwordInputs = screen.getAllByPlaceholderText('密码')
    fireEvent.change(passwordInputs[1], { target: { value: 'secret123' } })
    fireEvent.change(screen.getByPlaceholderText('确认密码'), { target: { value: 'secret123' } })
    fireEvent.click(findButtonByText('注册'))

    await waitFor(() => {
      expect(mockAuthService.register).toHaveBeenCalledWith({
        username: 'newuser',
        email: 'a@b.com',
        password: 'secret123',
        confirm: 'secret123',
      })
    })

    expect(screen.getByText('登录')).toBeInTheDocument()
  })
})
