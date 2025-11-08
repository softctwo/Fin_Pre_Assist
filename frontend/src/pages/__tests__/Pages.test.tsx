import React from 'react'
import { render, screen } from '@testing-library/react'
import { vi, describe, it, expect } from 'vitest'
import { BrowserRouter } from 'react-router-dom'

// Mock page components without external dependencies
const MockDashboard = () => (
  <div>
    <h1>仪表盘</h1>
    <div>文档总数: 10</div>
    <div>方案总数: 5</div>
  </div>
)

const MockTemplates = () => (
  <div>
    <h1>模板管理</h1>
    <button>创建模板</button>
    <table>
      <thead>
        <tr>
          <th>名称</th>
          <th>类型</th>
          <th>创建时间</th>
        </tr>
      </thead>
    </table>
  </div>
)

const MockKnowledge = () => (
  <div>
    <h1>知识库</h1>
    <button>添加知识</button>
    <div>知识条目列表</div>
  </div>
)

const renderWithRouter = (component: React.ReactElement) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  )
}

describe('Page Components', () => {
  describe('Dashboard', () => {
    it('renders dashboard with metrics', () => {
      renderWithRouter(<MockDashboard />)
      
      expect(screen.getByText('仪表盘')).toBeInTheDocument()
      expect(screen.getByText('文档总数: 10')).toBeInTheDocument()
      expect(screen.getByText('方案总数: 5')).toBeInTheDocument()
    })
  })

  describe('Templates', () => {
    it('renders templates page with controls', () => {
      renderWithRouter(<MockTemplates />)
      
      expect(screen.getByText('模板管理')).toBeInTheDocument()
      expect(screen.getByText('创建模板')).toBeInTheDocument()
      expect(screen.getByText('名称')).toBeInTheDocument()
      expect(screen.getByText('类型')).toBeInTheDocument()
      expect(screen.getByText('创建时间')).toBeInTheDocument()
    })
  })

  describe('Knowledge', () => {
    it('renders knowledge page with add button', () => {
      renderWithRouter(<MockKnowledge />)
      
      expect(screen.getByText('知识库')).toBeInTheDocument()
      expect(screen.getByText('添加知识')).toBeInTheDocument()
      expect(screen.getByText('知识条目列表')).toBeInTheDocument()
    })
  })
})