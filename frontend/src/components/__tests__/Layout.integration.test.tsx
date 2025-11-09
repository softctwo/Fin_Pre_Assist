import React from 'react'
import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import Layout from '../Layout'

const mockUseAuthStore = vi.hoisted(() =>
  vi.fn(() => ({
    user: { username: 'tester' },
    logout: vi.fn(),
  })),
)

vi.mock('../../store/authStore', () => ({
  useAuthStore: mockUseAuthStore,
}))

const mockNavigate = vi.hoisted(() => vi.fn())

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return {
    ...actual,
    useNavigate: () => mockNavigate,
    useLocation: () => ({ pathname: '/' }),
  }
})

vi.mock('antd', async () => {
  const actual = await vi.importActual('antd')
  return {
    ...actual,
    Dropdown: ({ menu, children }: any) => (
      <div>
        <div>{children}</div>
        <div data-testid="user-menu">
          {menu?.items
            ?.filter((item: any) => item?.key && item?.label)
            .map((item: any) => (
              <button key={item.key} onClick={item.onClick}>
                {item.label}
              </button>
            ))}
        </div>
      </div>
    ),
  }
})

const renderLayout = () =>
  render(
    <MemoryRouter initialEntries={['/']}>
      <Routes>
        <Route element={<Layout />}>
          <Route index element={<div>Home</div>} />
        </Route>
      </Routes>
    </MemoryRouter>,
  )

describe('Layout integration', () => {
  it('shows user information in header', () => {
    renderLayout()
    expect(screen.getByText('金融售前方案辅助系统')).toBeInTheDocument()
    expect(screen.getByText('tester')).toBeInTheDocument()
  })

  it('triggers logout menu item', () => {
    const logout = vi.fn()
    mockUseAuthStore.mockReturnValue({ user: { username: 'tester' }, logout })

    renderLayout()

    const logoutButton = screen.getByText('退出登录')
    fireEvent.click(logoutButton)

    expect(logout).toHaveBeenCalled()
    expect(mockNavigate).toHaveBeenCalledWith('/login')
  })
})
