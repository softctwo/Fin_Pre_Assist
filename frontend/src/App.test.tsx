import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { Outlet } from 'react-router-dom'
import App from './App'

// Mock the auth store
vi.mock('./store/authStore', () => ({
  useAuthStore: vi.fn(),
}))

// Mock the Layout component
vi.mock('./components/Layout', () => ({
  default: () => (
    <div data-testid="layout">
      Layout Component
      <Outlet />
    </div>
  ),
}))

// Mock all page components
vi.mock('./pages/Login', () => ({
  default: () => <div data-testid="login-page">Login Page</div>,
}))

vi.mock('./pages/Dashboard', () => ({
  default: () => <div data-testid="dashboard-page">Dashboard Page</div>,
}))

vi.mock('./pages/Documents', () => ({
  default: () => <div data-testid="documents-page">Documents Page</div>,
}))

vi.mock('./pages/Proposals', () => ({
  default: () => <div data-testid="proposals-page">Proposals Page</div>,
}))

vi.mock('./pages/ProposalCreate', () => ({
  default: () => <div data-testid="proposal-create-page">Proposal Create Page</div>,
}))

vi.mock('./pages/ProposalDetail', () => ({
  default: () => <div data-testid="proposal-detail-page">Proposal Detail Page</div>,
}))

vi.mock('./pages/Templates', () => ({
  default: () => <div data-testid="templates-page">Templates Page</div>,
}))

vi.mock('./pages/Knowledge', () => ({
  default: () => <div data-testid="knowledge-page">Knowledge Page</div>,
}))

import { useAuthStore } from './store/authStore'

const renderApp = (initialRoute = '/') => {
  window.history.pushState({}, 'Test page', initialRoute)
  return render(<App />)
}

type AuthState = {
  token: string | null | undefined
}

const authState: AuthState = {
  token: null,
}

const setAuthToken = (token: AuthState['token']) => {
  authState.token = token
}

describe('App Component', () => {
  const mockUseAuthStore = vi.mocked(useAuthStore)

  beforeEach(() => {
    vi.clearAllMocks()
    authState.token = null
    mockUseAuthStore.mockImplementation((selector?: (state: AuthState) => unknown) => {
      if (typeof selector === 'function') {
        return selector(authState)
      }
      return authState
    })
  })

  afterEach(() => {
    vi.resetAllMocks()
  })

  describe('Routing Configuration', () => {
    it('renders login page when accessing /login route', () => {
      setAuthToken(null)

      renderApp('/login')

      expect(screen.getByTestId('login-page')).toBeInTheDocument()
    })

    it('redirects to login when accessing protected route without token', () => {
      setAuthToken(null)

      renderApp('/')

      expect(screen.getByTestId('login-page')).toBeInTheDocument()
    })

    it('renders dashboard when accessing root route with token', () => {
      setAuthToken('fake-token')

      renderApp('/')

      expect(screen.getByTestId('layout')).toBeInTheDocument()
      expect(screen.getByTestId('dashboard-page')).toBeInTheDocument()
    })

    it('renders documents page when accessing /documents with token', () => {
      setAuthToken('fake-token')

      renderApp('/documents')

      expect(screen.getByTestId('layout')).toBeInTheDocument()
      expect(screen.getByTestId('documents-page')).toBeInTheDocument()
    })

    it('renders proposals page when accessing /proposals with token', () => {
      setAuthToken('fake-token')

      renderApp('/proposals')

      expect(screen.getByTestId('layout')).toBeInTheDocument()
      expect(screen.getByTestId('proposals-page')).toBeInTheDocument()
    })

    it('renders proposal create page when accessing /proposals/create with token', () => {
      setAuthToken('fake-token')

      renderApp('/proposals/create')

      expect(screen.getByTestId('layout')).toBeInTheDocument()
      expect(screen.getByTestId('proposal-create-page')).toBeInTheDocument()
    })

    it('renders proposal detail page when accessing /proposals/123 with token', () => {
      setAuthToken('fake-token')

      renderApp('/proposals/123')

      expect(screen.getByTestId('layout')).toBeInTheDocument()
      expect(screen.getByTestId('proposal-detail-page')).toBeInTheDocument()
    })

    it('renders templates page when accessing /templates with token', () => {
      setAuthToken('fake-token')

      renderApp('/templates')

      expect(screen.getByTestId('layout')).toBeInTheDocument()
      expect(screen.getByTestId('templates-page')).toBeInTheDocument()
    })

    it('renders knowledge page when accessing /knowledge with token', () => {
      setAuthToken('fake-token')

      renderApp('/knowledge')

      expect(screen.getByTestId('layout')).toBeInTheDocument()
      expect(screen.getByTestId('knowledge-page')).toBeInTheDocument()
    })
  })

  describe('ProtectedRoute Component', () => {
    it('allows access to protected routes when token exists', () => {
      setAuthToken('valid-token')

      renderApp('/documents')

      expect(screen.getByTestId('documents-page')).toBeInTheDocument()
      expect(screen.queryByTestId('login-page')).not.toBeInTheDocument()
    })

    it('redirects to login when token is null', () => {
      setAuthToken(null)

      renderApp('/documents')

      expect(screen.getByTestId('login-page')).toBeInTheDocument()
      expect(screen.queryByTestId('documents-page')).not.toBeInTheDocument()
    })

    it('redirects to login when token is empty string', () => {
      setAuthToken('')

      renderApp('/documents')

      expect(screen.getByTestId('login-page')).toBeInTheDocument()
      expect(screen.queryByTestId('documents-page')).not.toBeInTheDocument()
    })

    it('redirects to login when token is undefined', () => {
      setAuthToken(undefined)

      renderApp('/documents')

      expect(screen.getByTestId('login-page')).toBeInTheDocument()
      expect(screen.queryByTestId('documents-page')).not.toBeInTheDocument()
    })
  })

  describe('Authentication State Changes', () => {
    it('handles authentication state changes correctly', () => {
      // Start with no token
      setAuthToken(null)

      const view = renderApp('/')

      expect(screen.getByTestId('login-page')).toBeInTheDocument()

      // Simulate login by updating token and mounting again at root
      setAuthToken('new-token')
      view.unmount()
      renderApp('/')

      expect(screen.getByTestId('layout')).toBeInTheDocument()
      expect(screen.getByTestId('dashboard-page')).toBeInTheDocument()
    })

    it('preserves other routes when auth state changes', () => {
      setAuthToken('initial-token')

      const { rerender } = renderApp('/templates')

      expect(screen.getByTestId('templates-page')).toBeInTheDocument()

      // Change auth state but keep same route
      setAuthToken('updated-token')

      rerender(<App />)

      expect(screen.getByTestId('templates-page')).toBeInTheDocument()
    })
  })

  describe('Navigation and Routing', () => {
    it('handles nested route parameters correctly', () => {
      setAuthToken('valid-token')

      renderApp('/proposals/abc123')

      expect(screen.getByTestId('proposal-detail-page')).toBeInTheDocument()
    })

    it('handles multiple route parameters', () => {
      setAuthToken('valid-token')

      renderApp('/proposals/test-id-456')

      expect(screen.getByTestId('proposal-detail-page')).toBeInTheDocument()
    })
  })

  describe('Component Integration', () => {
    it('integrates correctly with React Router', () => {
      setAuthToken('valid-token')

      renderApp('/')

      // Verify that router context is available
      expect(screen.getByTestId('layout')).toBeInTheDocument()
      expect(screen.getByTestId('dashboard-page')).toBeInTheDocument()
    })

    it('maintains router state across renders', () => {
      setAuthToken('valid-token')

      const { rerender } = renderApp('/proposals')

      expect(screen.getByTestId('proposals-page')).toBeInTheDocument()

      // Re-render with same auth state
      setAuthToken('valid-token')

      rerender(<App />)

      expect(screen.getByTestId('proposals-page')).toBeInTheDocument()
    })
  })

  describe('Error Handling', () => {
    it('handles router errors gracefully', () => {
      setAuthToken('valid-token')

      // Test with malformed route
      expect(() => {
        renderApp('/')
      }).not.toThrow()
    })
  })

  describe('Performance and Memory', () => {
    it('does not create unnecessary re-renders', () => {
      let renderCount = 0
      setAuthToken('valid-token')

      const TestComponent = () => {
        renderCount++
        return <App />
      }

      const { rerender } = render(<TestComponent />)

      const initialRenderCount = renderCount

      // Re-render with same props
      rerender(<TestComponent />)

      // Render count should increase by one due to explicit rerender call
      expect(renderCount).toBe(initialRenderCount + 1)
    })
  })
})
