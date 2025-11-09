import React from "react";
import { useState, useEffect } from 'react'
import { Card, Descriptions, Button, Space, Tag, message, Spin } from 'antd'
import { useParams, useNavigate } from 'react-router-dom'
import { proposalService, type Proposal } from '../services/proposalService'
import { ThunderboltOutlined, DownloadOutlined } from '@ant-design/icons'
import ProposalGenerationProgress from '../components/ProposalGenerationProgress'
import { handleFileDownload } from '../utils/fileDownload'

const ProposalDetail = () => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [proposal, setProposal] = useState<Proposal | null>(null)
  const [loading, setLoading] = useState(false)
  const [generating, setGenerating] = useState(false)
  const [showProgress, setShowProgress] = useState(false)
  const [exporting, setExporting] = useState<string | null>(null)

  useEffect(() => {
    if (id) {
      loadProposal(parseInt(id))
    }
  }, [id])

  const loadProposal = async (proposalId: number) => {
    setLoading(true)
    try {
      const data = await proposalService.get(proposalId)
      setProposal(data)
    } catch (error) {
      console.error('加载方案失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleGenerate = async () => {
    if (!proposal) return

    // 显示进度弹窗并启动生成
    setShowProgress(true)
    setGenerating(true)
    
    try {
      // 后台开始生成,WebSocket会推送进度
      await proposalService.generate(proposal.id)
      // 注意:生成完成后由进度组件的onComplete处理
    } catch (error) {
      console.error('启动生成失败:', error)
      setShowProgress(false)
      setGenerating(false)
      message.error('启动生成失败,请稍后重试')
    }
  }
  
  const handleGenerateComplete = (success: boolean) => {
    setShowProgress(false)
    setGenerating(false)
    
    if (success) {
      message.success('方案生成成功!')
      // 重新加载方案数据
      if (proposal) {
        loadProposal(proposal.id)
      }
    }
  }
  
  const handleGenerateCancel = () => {
    setShowProgress(false)
    setGenerating(false)
    message.info('已取消生成')
  }

  const handleExport = async (format: string) => {
    if (!proposal) return

    setExporting(format)

    try {
      const response = await proposalService.export(proposal.id, format)

      // 处理文件下载
      const filename = `${proposal.title}.${format}`
      const success = handleFileDownload(response, filename)

      if (success) {
        message.success(`${format.toUpperCase()} 导出成功`)
      } else {
        message.error('导出失败：响应不是文件格式')
      }
    } catch (error: any) {
      console.error('导出失败:', error)
      // 处理认证错误
      if (error.response?.status === 401) {
        message.error('认证失败，请重新登录')
      } else if (error.response?.status === 403) {
        message.error('无权限导出此方案')
      } else if (error.response?.status === 404) {
        message.error('方案不存在或未完成生成')
      } else {
        message.error(`导出失败: ${error.message || '未知错误'}`)
      }
    } finally {
      setExporting(null)
    }
  }

  if (loading) {
    return <div style={{ textAlign: 'center', padding: 50 }}><Spin size="large" /></div>
  }

  if (!proposal) {
    return <div>方案不存在</div>
  }

  const statusMap: Record<string, { text: string, color: string }> = {
    draft: { text: '草稿', color: 'default' },
    generating: { text: '生成中', color: 'processing' },
    completed: { text: '已完成', color: 'success' },
    exported: { text: '已导出', color: 'cyan' },
  }
  const statusInfo = statusMap[proposal.status] || { text: proposal.status, color: 'default' }

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <h1>{proposal.title}</h1>
        <Space>
          {proposal.status === 'draft' && (
            <Button
              type="primary"
              icon={<ThunderboltOutlined />}
              onClick={handleGenerate}
              loading={generating}
            >
              生成方案
            </Button>
          )}
          {proposal.status === 'completed' && (
            <>
              <Button
                icon={<DownloadOutlined />}
                onClick={() => handleExport('docx')}
                loading={exporting === 'docx'}
              >
                导出Word
              </Button>
              <Button
                icon={<DownloadOutlined />}
                onClick={() => handleExport('pdf')}
                loading={exporting === 'pdf'}
              >
                导出PDF
              </Button>
              <Button
                icon={<DownloadOutlined />}
                onClick={() => handleExport('xlsx')}
                loading={exporting === 'xlsx'}
              >
                导出报价单
              </Button>
            </>
          )}
          <Button onClick={() => navigate('/proposals')}>返回</Button>
        </Space>
      </div>

      <Card title="基本信息" style={{ marginBottom: 16 }}>
        <Descriptions column={2}>
          <Descriptions.Item label="客户名称">{proposal.customer_name}</Descriptions.Item>
          <Descriptions.Item label="行业">{proposal.customer_industry || '-'}</Descriptions.Item>
          <Descriptions.Item label="状态">
            <Tag color={statusInfo.color}>{statusInfo.text}</Tag>
          </Descriptions.Item>
          <Descriptions.Item label="创建时间">
            {new Date(proposal.created_at).toLocaleString()}
          </Descriptions.Item>
        </Descriptions>
      </Card>

      <Card title="客户需求" style={{ marginBottom: 16 }}>
        <p style={{ whiteSpace: 'pre-wrap' }}>{proposal.requirements}</p>
      </Card>

      {proposal.executive_summary && (
        <Card title="执行摘要" style={{ marginBottom: 16 }}>
          <p style={{ whiteSpace: 'pre-wrap' }}>{proposal.executive_summary}</p>
        </Card>
      )}

      {proposal.solution_overview && (
        <Card title="解决方案概述" style={{ marginBottom: 16 }}>
          <p style={{ whiteSpace: 'pre-wrap' }}>{proposal.solution_overview}</p>
        </Card>
      )}

      {proposal.technical_details && (
        <Card title="技术细节" style={{ marginBottom: 16 }}>
          <p style={{ whiteSpace: 'pre-wrap' }}>{proposal.technical_details}</p>
        </Card>
      )}

      {proposal.implementation_plan && (
        <Card title="实施计划">
          <p style={{ whiteSpace: 'pre-wrap' }}>{proposal.implementation_plan}</p>
        </Card>
      )}
      
      {/* 进度弹窗 */}
      {proposal && (
        <ProposalGenerationProgress
          visible={showProgress}
          proposalId={proposal.id}
          onComplete={handleGenerateComplete}
          onCancel={handleGenerateCancel}
        />
      )}
    </div>
  )
}

export default ProposalDetail
