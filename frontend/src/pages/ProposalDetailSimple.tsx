import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  Card,
  Button,
  Descriptions,
  Space,
  message,
  Spin,
  Tag,
  Typography,
  Row,
  Col,
  Breadcrumb,
  Modal,
  Select,
  Form,
  Alert,
  Tabs,
  Input
} from 'antd'
import {
  ArrowLeftOutlined,
  FileTextOutlined,
  RobotOutlined,
  FileWordOutlined,
  FilePdfOutlined,
  FileExcelOutlined,
  DownloadOutlined
} from '@ant-design/icons'

const { Title, Paragraph } = Typography
const { Option } = Select
const { TabPane } = Tabs
const { TextArea } = Input

interface ProposalDetail {
  id: string
  title: string
  customer_name: string
  customer_industry: string
  status: string
  requirements: string
  content?: string
  executive_summary?: string
  solution_overview?: string
  technical_details?: string
  implementation_plan?: string
  pricing?: any
  created_at: string
  updated_at: string
}

const ProposalDetailSimple: React.FC = () => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [proposal, setProposal] = useState<ProposalDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [generatingContent, setGeneratingContent] = useState(false)
  const [showGenerateModal, setShowGenerateModal] = useState(false)
  const [token, setToken] = useState<string>('')
  const [activeTab, setActiveTab] = useState('detail')

  // 获取认证token
  useEffect(() => {
    const storedToken = localStorage.getItem('auth_token')
    if (storedToken) {
      setToken(storedToken)
    } else {
      navigate('/login')
    }
  }, [navigate])

  // 加载方案详情
  const loadProposalDetail = async () => {
    if (!id || !token) return

    try {
      setLoading(true)
      const response = await fetch(`/api/v1/proposals/${id}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (response.ok) {
        const data = await response.json()
        setProposal(data)
      } else {
        message.error('获取方案详情失败')
        navigate('/dashboard')
      }
    } catch (error) {
      console.error('加载方案详情错误:', error)
      message.error('网络错误，无法获取方案详情')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (id && token) {
      loadProposalDetail()
    }
  }, [id, token])

  // 生成方案内容
  const handleGenerateContent = async (values: any) => {
    if (!proposal) return

    setGeneratingContent(true)
    try {
      const response = await fetch(`/api/v1/proposals/${proposal.id}/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        }
      })

      if (response.ok) {
        const result = await response.json()
        message.success('方案内容生成成功！')
        setShowGenerateModal(false)
        // 重新加载方案详情
        await loadProposalDetail()
        setActiveTab('content')
      } else {
        const errorData = await response.json()
        message.error(errorData.detail || '生成方案内容失败')
      }
    } catch (error) {
      console.error('生成方案内容错误:', error)
      message.error('网络错误，生成方案内容失败')
    } finally {
      setGeneratingContent(false)
    }
  }

  // 导出功能
  const handleExport = async (format: 'word' | 'pdf' | 'excel') => {
    if (!proposal) return

    try {
      const response = await fetch(`/api/v1/proposals/${proposal.id}/export?format=${format}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (response.ok) {
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.style.display = 'none'
        a.href = url
        a.download = `${proposal.title}.${format === 'word' ? 'docx' : format === 'pdf' ? 'pdf' : 'xlsx'}`
        document.body.appendChild(a)
        a.click()
        window.URL.revokeObjectURL(url)
        document.body.removeChild(a)
        message.success(`导出${format.toUpperCase()}成功`)
      } else {
        message.error(`导出${format.toUpperCase()}失败`)
      }
    } catch (error) {
      console.error('导出错误:', error)
      message.error('导出失败，请重试')
    }
  }

  // 获取状态颜色
  const getStatusColor = (status: string) => {
    const statusColors: { [key: string]: string } = {
      'draft': 'default',
      'review': 'processing',
      'approved': 'success',
      'rejected': 'error',
      'completed': 'success',
      'generating': 'processing'
    }
    return statusColors[status] || 'default'
  }

  // 获取状态文本
  const getStatusText = (status: string) => {
    const statusTexts: { [key: string]: string } = {
      'draft': '草稿',
      'review': '审核中',
      'approved': '已通过',
      'rejected': '已拒绝',
      'completed': '已完成',
      'generating': '生成中'
    }
    return statusTexts[status] || status
  }

  if (loading) {
    return (
      <div style={{ padding: '50px', textAlign: 'center' }}>
        <Spin size="large" />
        <div style={{ marginTop: 16 }}>正在加载方案详情...</div>
      </div>
    )
  }

  if (!proposal) {
    return (
      <div style={{ padding: '50px', textAlign: 'center' }}>
        <Alert
          message="方案不存在"
          description="请检查方案ID是否正确"
          type="error"
          showIcon
        />
      </div>
    )
  }

  return (
    <div style={{ padding: '24px', background: '#f0f2f5', minHeight: '100vh' }}>
      {/* 顶部导航 */}
      <Row justify="space-between" align="middle" style={{ marginBottom: '24px' }}>
        <Col>
          <Breadcrumb>
            <Breadcrumb.Item>
              <Button
                type="text"
                icon={<ArrowLeftOutlined />}
                onClick={() => navigate('/dashboard')}
              >
                返回方案列表
              </Button>
            </Breadcrumb.Item>
            <Breadcrumb.Item>方案详情</Breadcrumb.Item>
            <Breadcrumb.Item>{proposal.title}</Breadcrumb.Item>
          </Breadcrumb>
        </Col>
        <Col>
          <Space>
            <Button
              type="primary"
              icon={<RobotOutlined />}
              onClick={() => setShowGenerateModal(true)}
            >
              生成方案内容
            </Button>
            {proposal.content && (
              <>
                <Button
                  icon={<FileWordOutlined />}
                  onClick={() => handleExport('word')}
                >
                  导出Word
                </Button>
                <Button
                  icon={<FilePdfOutlined />}
                  onClick={() => handleExport('pdf')}
                >
                  导出PDF
                </Button>
                <Button
                  icon={<FileExcelOutlined />}
                  onClick={() => handleExport('excel')}
                >
                  导出报价单
                </Button>
              </>
            )}
          </Space>
        </Col>
      </Row>

      {/* 方案基本信息 */}
      <Card style={{ marginBottom: '24px' }}>
        <Row justify="space-between" align="middle">
          <Col>
            <Space>
              <Title level={3} style={{ margin: 0 }}>{proposal.title}</Title>
              <Tag color={getStatusColor(proposal.status)}>
                {getStatusText(proposal.status)}
              </Tag>
            </Space>
          </Col>
        </Row>
      </Card>

      {/* 详细信息标签页 */}
      <Card>
        <Tabs activeKey={activeTab} onChange={setActiveTab}>
          <TabPane tab="基本信息" key="detail">
            <Descriptions bordered column={2}>
              <Descriptions.Item label="方案标题">{proposal.title}</Descriptions.Item>
              <Descriptions.Item label="客户名称">{proposal.customer_name}</Descriptions.Item>
              <Descriptions.Item label="所属行业">{proposal.customer_industry}</Descriptions.Item>
              <Descriptions.Item label="方案状态">
                <Tag color={getStatusColor(proposal.status)}>
                  {getStatusText(proposal.status)}
                </Tag>
              </Descriptions.Item>
              <Descriptions.Item label="创建时间">
                {new Date(proposal.created_at).toLocaleString()}
              </Descriptions.Item>
              <Descriptions.Item label="更新时间">
                {new Date(proposal.updated_at).toLocaleString()}
              </Descriptions.Item>
              <Descriptions.Item label="客户需求" span={2}>
                <Paragraph style={{ margin: 0 }}>
                  {proposal.requirements || '暂无需求描述'}
                </Paragraph>
              </Descriptions.Item>
            </Descriptions>
          </TabPane>

          <TabPane tab="方案内容" key="content">
            {proposal.content ? (
              <div style={{ minHeight: '400px' }}>
                <div
                  style={{
                    padding: '16px',
                    background: '#fafafa',
                    borderRadius: '6px',
                    lineHeight: '1.8',
                    fontSize: '14px',
                    whiteSpace: 'pre-wrap'
                  }}
                >
                  {proposal.content}
                </div>
              </div>
            ) : (
              <div style={{ textAlign: 'center', padding: '60px' }}>
                <FileTextOutlined style={{ fontSize: '48px', color: '#d9d9d9' }} />
                <div style={{ marginTop: '16px', color: '#999' }}>
                  暂无方案内容，请先生成方案内容
                </div>
                <Button
                  type="primary"
                  icon={<RobotOutlined />}
                  onClick={() => setShowGenerateModal(true)}
                  style={{ marginTop: '16px' }}
                >
                  生成方案内容
                </Button>
              </div>
            )}
          </TabPane>

          {proposal.executive_summary && (
            <TabPane tab="执行摘要" key="executive">
              <div style={{ padding: '16px', background: '#f0f8ff', borderRadius: '6px' }}>
                <Paragraph style={{ whiteSpace: 'pre-wrap' }}>
                  {proposal.executive_summary}
                </Paragraph>
              </div>
            </TabPane>
          )}

          {proposal.solution_overview && (
            <TabPane tab="解决方案概述" key="solution">
              <div style={{ padding: '16px', background: '#f9f9f9', borderRadius: '6px' }}>
                <Paragraph style={{ whiteSpace: 'pre-wrap' }}>
                  {proposal.solution_overview}
                </Paragraph>
              </div>
            </TabPane>
          )}

          {proposal.technical_details && (
            <TabPane tab="技术细节" key="technical">
              <div style={{ padding: '16px', background: '#f5f5f5', borderRadius: '6px' }}>
                <Paragraph style={{ whiteSpace: 'pre-wrap' }}>
                  {proposal.technical_details}
                </Paragraph>
              </div>
            </TabPane>
          )}

          {proposal.implementation_plan && (
            <TabPane tab="实施计划" key="implementation">
              <div style={{ padding: '16px', background: '#f0f9ff', borderRadius: '6px' }}>
                <Paragraph style={{ whiteSpace: 'pre-wrap' }}>
                  {proposal.implementation_plan}
                </Paragraph>
              </div>
            </TabPane>
          )}
        </Tabs>
      </Card>

      {/* 生成内容模态框 */}
      <Modal
        title="生成方案内容"
        open={showGenerateModal}
        onCancel={() => setShowGenerateModal(false)}
        footer={null}
        width={600}
      >
        <Form
          layout="vertical"
          onFinish={handleGenerateContent}
        >
          <Form.Item
            label="生成要求"
            name="requirements"
            initialValue={proposal.requirements}
            help="可以修改或补充客户需求说明"
          >
            <TextArea
              rows={4}
              placeholder="请描述具体的方案生成要求..."
            />
          </Form.Item>

          <Form.Item
            label="自定义提示"
            name="custom_prompt"
            help="可选：提供更具体的生成指导，如方案风格、重点内容等"
          >
            <TextArea
              rows={3}
              placeholder="可选的自定义提示词..."
            />
          </Form.Item>

          <Form.Item>
            <Space>
              <Button
                type="primary"
                htmlType="submit"
                loading={generatingContent}
                icon={<RobotOutlined />}
              >
                {generatingContent ? '生成中...' : '开始生成'}
              </Button>
              <Button onClick={() => setShowGenerateModal(false)}>
                取消
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

export default ProposalDetailSimple