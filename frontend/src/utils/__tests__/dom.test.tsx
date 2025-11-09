import React from 'react'
import { render, screen, fireEvent } from '@testing-library/react'
import { vi, describe, it, expect } from 'vitest'
import { ConfigProvider } from 'antd'
import { MemoryRouter } from 'react-router-dom'

// Mock WebSocket
global.WebSocket = vi.fn()

// Test helper to render with providers
const renderWithProviders = (component: React.ReactElement) => {
  return render(
    <MemoryRouter>
      <ConfigProvider>
        {component}
      </ConfigProvider>
    </MemoryRouter>
  )
}

describe('Basic DOM Tests', () => {
  it('renders div element correctly', () => {
    const TestComponent = () => <div data-testid="test">Hello World</div>
    renderWithProviders(<TestComponent />)
    expect(screen.getByTestId('test')).toBeInTheDocument()
    expect(screen.getByText('Hello World')).toBeInTheDocument()
  })

  it('renders different HTML elements', () => {
    const TestComponent = () => (
      <div>
        <h1>Title</h1>
        <p>Paragraph</p>
        <button>Button</button>
        <input placeholder="Input" />
      </div>
    )
    renderWithProviders(<TestComponent />)
    
    expect(screen.getByText('Title')).toBeInTheDocument()
    expect(screen.getByText('Paragraph')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Button' })).toBeInTheDocument()
    expect(screen.getByPlaceholderText('Input')).toBeInTheDocument()
  })
})

describe('Component Props Tests', () => {
  it('handles boolean props correctly', () => {
    const TestComponent = ({ show = true }: { show?: boolean }) => 
      show ? <div data-testid="content">Visible</div> : null
    
    const { rerender } = render(<TestComponent show={true} />)
    expect(screen.getByTestId('content')).toBeInTheDocument()

    rerender(<TestComponent show={false} />)
    expect(screen.queryByTestId('content')).not.toBeInTheDocument()
  })

  it('handles array props correctly', () => {
    const ListComponent = ({ items = [] }: { items?: string[] }) => (
      <ul data-testid="list">
        {items.map((item, index) => (
          <li key={index} data-testid={`item-${index}`}>{item}</li>
        ))}
      </ul>
    )

    const { rerender } = render(<ListComponent items={['a', 'b', 'c']} />)
    expect(screen.getByTestId('item-0')).toHaveTextContent('a')
    expect(screen.getByTestId('item-1')).toHaveTextContent('b')
    expect(screen.getByTestId('item-2')).toHaveTextContent('c')

    rerender(<ListComponent items={[]} />)
    expect(screen.getByTestId('list')).toBeEmptyDOMElement()
  })

  it('handles function props correctly', () => {
    const ButtonComponent = ({ onClick, children }: any) => (
      <button data-testid="button" onClick={onClick}>
        {children}
      </button>
    )

    const handleClick = vi.fn()
    render(<ButtonComponent onClick={handleClick}>Click me</ButtonComponent>)

    const button = screen.getByTestId('button')
    fireEvent.click(button)

    expect(handleClick).toHaveBeenCalledTimes(1)
  })
})

describe('Form Validation Tests', () => {
  it('shows error for required fields', async () => {
    const FormComponent = () => {
      const [error, setError] = React.useState<string>('')
      
      const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault()
        const input = e.target as any
        if (!input.value?.trim()) {
          setError('This field is required')
        } else {
          setError('')
        }
      }
      
      return (
        <form onSubmit={handleSubmit}>
          <input data-testid="input" name="test" />
          <button type="submit" data-testid="submit">Submit</button>
          {error && <span data-testid="error">{error}</span>}
        </form>
      )
    }

    render(<FormComponent />)
    
    const submitButton = screen.getByTestId('submit')
    fireEvent.click(submitButton)

    expect(screen.getByTestId('error')).toBeInTheDocument()
    expect(screen.getByTestId('error')).toHaveTextContent('This field is required')
  })
})

describe('Modal Tests', () => {
  it('renders modal when visible', () => {
    const ModalComponent = ({ visible }: { visible: boolean }) => (
      visible ? (
        <div data-testid="modal">
          <div>Modal Content</div>
          <button data-testid="close">Close</button>
        </div>
      ) : null
    )

    const { rerender } = render(<ModalComponent visible={true} />)
    expect(screen.getByTestId('modal')).toBeInTheDocument()
    expect(screen.getByText('Modal Content')).toBeInTheDocument()

    rerender(<ModalComponent visible={false} />)
    expect(screen.queryByTestId('modal')).not.toBeInTheDocument()
  })
})

describe('Loading States Tests', () => {
  it('shows loading spinner', () => {
    const LoadingComponent = ({ loading }: { loading: boolean }) => (
      loading ? <div data-testid="loading">Loading...</div> : <div data-testid="content">Content</div>
    )

    const { rerender } = render(<LoadingComponent loading={true} />)
    expect(screen.getByTestId('loading')).toBeInTheDocument()
    expect(screen.queryByTestId('content')).not.toBeInTheDocument()

    rerender(<LoadingComponent loading={false} />)
    expect(screen.queryByTestId('loading')).not.toBeInTheDocument()
    expect(screen.getByTestId('content')).toBeInTheDocument()
  })
})
