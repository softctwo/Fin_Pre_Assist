import { useState, useEffect } from 'react'
import { Card, Descriptions, Button, Space, Tag, message, Spin } from 'antd'
import { useParams, useNavigate } from 'react-router-dom'
import { proposalService, type Proposal } from '../services/proposalService'
import { ThunderboltOutlined, DownloadOutlined } from '@ant-design/icons'

const ProposalDetail = () => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [proposal, setProposal] = useState<Proposal | null>(null)
  const [loading, setLoading] = useState(false)
  const [generating, setGenerating] = useState(false)

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

    setGenerating(true)
    try {
      const data = await proposalService.generate(proposal.id)
      setProposal(data)
      message.success('方案生成成功')
    } catch (error) {
      console.error('生成失败:', error)
    } finally {
      setGenerating(false)
    }
  }

  const handleExport = async (format: string) => {
    if (!proposal) return

    try {
      await proposalService.export(proposal.id, format)
      message.success('导出成功')
    } catch (error) {
      console.error('导出失败:', error)
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
                onClick={() => window.open(`/api/v1/proposals/${proposal.id}/export?format=docx`, '_blank')}
              >
                导出Word
              </Button>
              <Button
                icon={<DownloadOutlined />}
                onClick={() => window.open(`/api/v1/proposals/${proposal.id}/export?format=xlsx`, '_blank')}
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
    </div>
  )
}

export default ProposalDetail
