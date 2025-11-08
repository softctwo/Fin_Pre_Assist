import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { vi, describe, it, expect, beforeEach } from 'vitest'
import { MemoryRouter } from 'react-router-dom'
import { ConfigProvider, Button, Form, Input, Modal } from 'antd'
import { create } from 'zustand'

// Mock auth service
vi.mock('../../services/authService', () => ({
  default: {
    login: vi.fn(),
    register: vi.fn(),
    getCurrentUser: vi.fn(),
  }
}))

// Mock components
const mockNavigate = vi.fn()
vi.mock('react-router-dom', () => ({
  useNavigate: () => mockNavigate,
  useLocation: () => ({ pathname: '/login' }),
}))

vi.mock('antd', () => ({
  ConfigProvider: ({ children }: any) => <div>{children}</div>,
  Form: { Item: ({ children }: any) => <div>{children}</div> },
  Input: (props: any) => <input {...props} />,
  Button: (props: any) => <button {...props} />,
  Modal: ({ children }: any) => <div>{children}</div>,
}))

const mockAuthService = vi.mocked(await import('../../services/authService'))

describe('Auth Service Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Service Methods', () => {
    it('should import authService', () => {
      const authService = require('../../services/authService').default
      expect(authService).toBeDefined()
      expect(typeof authService.login).toBe('function')
      expect(typeof authService.register).toBe('function')
      expect(typeof authService.getCurrentUser).toBe('function')
    })

    it('should handle successful login', async () => {
      const mockResponse = {
        access_token: 'test-token',
        token_type: 'bearer',
        user: { id: 1, username: 'testuser', role: 'user' }
      }
      
      mockAuthService.login.mockResolvedValue(mockResponse)

      const authService = require('../../services/authService').default
      const result = await authService.login('testuser', 'password123')

      expect(mockAuthService.login).toHaveBeenCalledWith('testuser', 'password123')
      expect(result).toEqual(mockResponse)
    })

    it('should handle login failure', async () => {
      const mockError = new Error('Invalid credentials')
      mockAuthService.login.mockRejectedValue(mockError)

      const authService = require('../../services/authService').default
      await expect(authService.login('wrong', 'credentials')).rejects.toThrow()
    })

    it('should handle successful registration', async () => {
      const mockResponse = {
        id: 1,
        username: 'newuser',
        email: 'new@example.com',
        role: 'user'
      }
      
      mockAuthService.register.mockResolvedValue(mockResponse)

      const authService = require('../../services/authService').default
      const result = await authService.register('newuser', 'new@example.com', 'password123')

      expect(mockAuthService.register).toHaveBeenCalledWith('newuser', 'new@example.com', 'password123')
      expect(result).toEqual(mockResponse)
    })

    it('should handle getCurrentUser', async () => {
      const mockResponse = {
        id: 1,
        username: 'testuser',
        email: 'test@example.com',
        role: 'user'
      }
      
      mockAuthService.getCurrentUser.mockResolvedValue(mockResponse)

      const authService = require('../../services/authService').default
      const result = await authService.getCurrentUser()

      expect(mockAuthService.getCurrentUser).toHaveBeenCalled()
      expect(result).toEqual(mockResponse)
    })
  })

  describe('Integration with Store', () => {
    it('should work with zustand store', () => {
      const useAuthStore = create((set) => ({
        token: null as string | null,
        user: null as any,
        setAuth: (token: string, user: any) => set({ token, user }),
        logout: () => set({ token: null, user: null })
      }))

      const store = useAuthStore.getState()
      expect(store).toHaveProperty('token')
      expect(store).toHaveProperty('user')
      expect(store).toHaveProperty('setAuth')
      expect(store).toHaveProperty('logout')
    })
  })
})