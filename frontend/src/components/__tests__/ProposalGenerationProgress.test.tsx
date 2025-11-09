import React from 'react'
import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { MemoryRouter } from 'react-router-dom'
import { ConfigProvider } from 'antd'
import ProposalGenerationProgress from '../ProposalGenerationProgress'

const mockUseAuthStore = vi.hoisted(() =>
  vi.fn(() => ({
    user: { id: 1, username: 'tester' },
  })),
)

vi.mock('../../store/authStore', () => ({
  useAuthStore: mockUseAuthStore,
}))

const mockWebSocket = {
  close: vi.fn(),
  send: vi.fn(),
  addEventListener: vi.fn(),
  removeEventListener: vi.fn(),
  readyState: 1,
}

global.WebSocket = vi.fn().mockImplementation(() => mockWebSocket) as any

const renderModal = (props: Partial<React.ComponentProps<typeof ProposalGenerationProgress>> = {}) =>
  render(
    <ConfigProvider>
      <MemoryRouter>
        <ProposalGenerationProgress
          visible={true}
          proposalId={1}
          onCancel={vi.fn()}
          onComplete={vi.fn()}
          {...props}
        />
      </MemoryRouter>
    </ConfigProvider>,
  )

describe('ProposalGenerationProgress (lightweight)', () => {
  it('does not render when invisible', () => {
    renderModal({ visible: false })
    expect(screen.queryByText('方案生成中')).not.toBeInTheDocument()
  })

  it('renders modal title when visible', () => {
    renderModal()
    expect(screen.getByText('方案生成中')).toBeInTheDocument()
  })

})
