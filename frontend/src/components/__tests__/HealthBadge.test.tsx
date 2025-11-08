import { render, screen } from '@testing-library/react'
import { vi, describe, it, expect } from 'vitest'

describe('dummy health badge', () => {
  it('renders placeholder', () => {
    render(<div data-testid="health-badge">OK</div>)
    expect(screen.getByTestId('health-badge').textContent).toBe('OK')
  })
})
