import React, { useState, useEffect } from 'react'
import { Card, Select, Button, Form, Input, message, Space, Table, Tag, Rate, Modal, Tabs, Progress, Spin, Divider } from 'antd'
import { RobotOutlined, ThunderboltOutlined, BranchesOutlined, CompareOutlined, EyeOutlined, EditOutlined } from '@ant-design/icons'
import { multiModelProposalService } from '../services/multiModelProposalService'

const { TextArea } = Input
const { Option } = Select
const { TabPane } = Tabs

interface Model {
  provider: string
  name: string
  model: string
  available: boolean
}

interface ProposalVersion {
  id: number
  proposal_id: number
  version_number: number
  title: string
  model_provider: string
  model_name: string
  status: 'draft' | 'generating' | 'completed' | 'failed' | 'selected'
  parent_version_id?: number
  generation_time?: string
  generation_duration?: number
  tokens_used?: number
  user_rating?: number
  created_at: string
  content_summary?: {
    executive_summary?: string
    solution_overview?: string
    key_points?: string[]
    estimated_duration?: string
    estimated_cost?: string
  }
}

interface MultiModelProposalGeneratorProps {
  proposalId: number
  onGenerationComplete?: (versions: ProposalVersion[]) => void
}

const MultiModelProposalGenerator: React.FC<MultiModelProposalGeneratorProps> = ({
  proposalId,
  onGenerationComplete
}) => {
  const [form] = Form.useForm()
  const [models, setModels] = useState<Model[]>([])
  const [selectedModels, setSelectedModels] = useState<string[]>([])
  const [generating, setGenerating] = useState(false)
  const [versions, setVersions] = useState<ProposalVersion[]>([])
  const [selectedVersion, setSelectedVersion] = useState<ProposalVersion | null>(null)
  const [comparisonModalVisible, setComparisonModalVisible] = useState(false)
  const [compareVersions, setCompareVersions] = useState<ProposalVersion[]>([])
  const [activeTab, setActiveTab] = useState('generate')
  const [iterationModalVisible, setIterationModalVisible] = useState(false)
  const [iterationFeedback, setIterationFeedback] = useState('')
  const [iterationModel, setIterationModel] = useState<string[]>([])

  // 加载可用模型
  useEffect(() => {
    loadModels()
    loadVersions()
  }, [proposalId])

  const loadModels = async () => {
    try {
      const response = await multiModelProposalService.getAvailableModels()
      setModels(response)
    } catch (error) {
      message.error('加载模型列表失败')
    }
  }

  const loadVersions = async () => {
    try {
      const response = await multiModelProposalService.getProposalVersions(proposalId)
      setVersions(response)
    } catch (error) {
      message.error('加载版本列表失败')
    }
  }

  const handleGenerate = async (values: any) => {
    if (selectedModels.length === 0) {
      message.warning('请选择至少一个AI模型')
      return
    }

    setGenerating(true)
    try {
      await multiModelProposalService.generateProposalVersions({
        proposalId,
        selectedModels,
        requirements: values.requirements
      })

      message.success('方案生成任务已启动')

      // 定期检查生成状态
      const checkInterval = setInterval(async () => {
        await loadVersions()

        const completedVersions = await multiModelProposalService.getProposalVersions(proposalId)
        const allCompleted = completedVersions.every(v =>
          v.status === 'completed' || v.status === 'failed'
        )

        if (allCompleted) {
          clearInterval(checkInterval)
          setGenerating(false)
          loadVersions()
          if (onGenerationComplete) {
            onGenerationComplete(completedVersions)
          }
        }
      }, 2000)

    } catch (error) {
      message.error('生成方案失败')
      setGenerating(false)
    }
  }

  const handleIterate = async () => {
    if (!selectedVersion) {
      message.warning('请选择要迭代的版本')
      return
    }
    if (!iterationFeedback.trim()) {
      message.warning('请输入迭代反馈')
      return
    }
    if (iterationModel.length === 0) {
      message.warning('请选择生成模型')
      return
    }

    try {
      await multiModelProposalService.iterateVersion({
        versionId: selectedVersion.id,
        feedback: iterationFeedback,
        selectedModels: iterationModel
      })

      message.success('迭代任务已启动')
      setIterationModalVisible(false)
      setIterationFeedback('')
      loadVersions()
    } catch (error) {
      message.error('迭代失败')
    }
  }

  const handleCompare = async () => {
    if (compareVersions.length < 2) {
      message.warning('请选择至少2个版本进行对比')
      return
    }

    try {
      const comparison = await multiModelProposalService.compareVersions(
        compareVersions.map(v => v.id)
      )

      console.log('版本对比结果:', comparison)
      message.success('版本对比完成')
    } catch (error) {
      message.error('版本对比失败')
    }
  }

  const handleRateVersion = async (versionId: number, rating: number) => {
    try {
      await multiModelProposalService.rateVersion(versionId, rating)
      message.success('评分成功')
      loadVersions()
    } catch (error) {
      message.error('评分失败')
    }
  }

  const handleSelectVersion = async (versionId: number) => {
    try {
      await multiModelProposalService.selectVersion(versionId)
      message.success('版本已选定')
      loadVersions()
    } catch (error) {
      message.error('选定版本失败')
    }
  }

  const getStatusTag = (status: string) => {
    const statusMap = {
      draft: { color: 'default', text: '草稿' },
      generating: { color: 'processing', text: '生成中' },
      completed: { color: 'success', text: '已完成' },
      failed: { color: 'error', text: '失败' },
      selected: { color: 'gold', text: '已选中' }
    }
    const config = statusMap[status as keyof typeof statusMap] || statusMap.draft
    return <Tag color={config.color}>{config.text}</Tag>
  }

  const columns = [
    {
      title: '版本号',
      dataIndex: 'version_number',
      key: 'version_number',
      render: (num: number, record: ProposalVersion) => (
        <span>
          v{num}
          {record.status === 'selected' && <Tag color="gold" size="small">主版本</Tag>}
        </span>
      )
    },
    {
      title: '模型',
      dataIndex: 'model_provider',
      key: 'model_provider',
      render: (provider: string, record: ProposalVersion) => {
        const modelNames: Record<string, string> = {
          kimi: 'Kimi',
          zhipu: '智谱AI',
          deepseek: 'DeepSeek'
        }
        return `${modelNames[provider] || provider} (${record.model_name})`
      }
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: getStatusTag
    },
    {
      title: '生成耗时',
      dataIndex: 'generation_duration',
      key: 'generation_duration',
      render: (duration?: number) => duration ? `${duration}秒` : '-'
    },
    {
      title: '用户评分',
      dataIndex: 'user_rating',
      key: 'user_rating',
      render: (rating?: number, record: ProposalVersion) => (
        <Rate
          defaultValue={rating}
          onChange={(value) => handleRateVersion(record.id, value || 0)}
          disabled={record.status !== 'completed'}
        />
      )
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: ProposalVersion) => (
        <Space>
          <Button
            type="link"
            icon={<EyeOutlined />}
            size="small"
            onClick={() => setSelectedVersion(record)}
          >
            查看
          </Button>
          <Button
            type="link"
            icon={<EditOutlined />}
            size="small"
            onClick={() => {
              setSelectedVersion(record)
              setIterationModalVisible(true)
            }}
            disabled={record.status !== 'completed'}
          >
            迭代
          </Button>
          <Button
            type="link"
            icon={<CompareOutlined />}
            size="small"
            onClick={() => {
              const existingVersions = compareVersions.filter(v => v.id !== record.id)
              setCompareVersions([...existingVersions, record])
              setComparisonModalVisible(true)
            }}
          >
            对比
          </Button>
          <Button
            type="link"
            size="small"
            onClick={() => handleSelectVersion(record.id)}
            disabled={record.status === 'selected'}
          >
            选定
          </Button>
        </Space>
      )
    }
  ]

  const getGenerationProgress = () => {
    if (!generating) return null

    const completedCount = versions.filter(v =>
      v.status === 'completed' || v.status === 'failed'
    ).length
    const totalCount = selectedModels.length
    const progress = (completedCount / totalCount) * 100

    return (
      <Card title="生成进度" style={{ marginTop: 16 }}>
        <Progress
          percent={progress}
          status={progress === 100 ? 'success' : 'active'}
          format={() => `${completedCount}/${totalCount} 版本`}
        />
      </Card>
    )
  }

  return (
    <div>
      <Tabs activeKey={activeTab} onChange={setActiveTab}>
        <TabPane
          tab={
            <span>
              <ThunderboltOutlined />
              多模型生成
            </span>
          }
          key="generate"
        >
          <Card title="多模型方案生成器" extra={<BranchesOutlined />}>
            <Form form={form} layout="vertical" onFinish={handleGenerate}>
              <Form.Item
                label="选择AI模型"
                required
                extra={`已选择 ${selectedModels.length} 个模型`}
              >
                <Select
                  mode="multiple"
                  placeholder="请选择要使用的AI模型"
                  style={{ width: '100%' }}
                  value={selectedModels}
                  onChange={setSelectedModels}
                >
                  {models.map(model => (
                    <Option key={model.provider} value={model.provider}>
                      <Space>
                        <RobotOutlined />
                        {model.name} ({model.model})
                        {model.available ? (
                          <Tag color="green" size="small">可用</Tag>
                        ) : (
                          <Tag color="red" size="small">不可用</Tag>
                        )}
                      </Space>
                    </Option>
                  ))}
                </Select>
              </Form.Item>

              <Form.Item
                label="需求描述"
                name="requirements"
                rules={[{ required: true, message: '请输入需求描述' }]}
                extra="详细描述客户需求和背景信息"
              >
                <TextArea
                  rows={4}
                  placeholder="请详细描述客户需求、项目背景、期望目标等..."
                />
              </Form.Item>

              <Form.Item>
                <Space>
                  <Button
                    type="primary"
                    htmlType="submit"
                    loading={generating}
                    icon={<ThunderboltOutlined />}
                    disabled={selectedModels.length === 0}
                  >
                    {generating ? '生成中...' : '开始生成'}
                  </Button>
                  <Button onClick={() => form.resetFields()}>
                    重置
                  </Button>
                </Space>
              </Form.Item>
            </Form>
          </Card>

          {getGenerationProgress()}

          {versions.length > 0 && (
            <Card title="生成历史" style={{ marginTop: 16 }}>
              <Table
                columns={columns}
                dataSource={versions}
                rowKey="id"
                pagination={{ pageSize: 10 }}
              />
            </Card>
          )}
        </TabPane>

        <TabPane
          tab={
            <span>
              <CompareOutlined />
              版本对比
            </span>
          }
          key="compare"
        >
          <Card title="版本对比分析">
            <div style={{ textAlign: 'center', padding: '40px 0' }}>
              <BranchesOutlined style={{ fontSize: '48px', color: '#ccc' }} />
              <p style={{ marginTop: 16, color: '#999' }}>
                在版本列表中选择版本进行对比，或使用批量对比功能
              </p>
            </div>
          </Card>
        </TabPane>
      </Tabs>

      {/* 版本详情弹窗 */}
      <Modal
        title={`版本详情 - ${selectedVersion?.title}`}
        open={!!selectedVersion}
        onCancel={() => setSelectedVersion(null)}
        width={800}
        footer={[
          <Button key="close" onClick={() => setSelectedVersion(null)}>
            关闭
          </Button>
        ]}
      >
        {selectedVersion && (
          <div>
            <Divider>基本信息</Divider>
            <p><strong>版本号:</strong> v{selectedVersion.version_number}</p>
            <p><strong>AI模型:</strong> {selectedVersion.model_provider} - {selectedVersion.model_name}</p>
            <p><strong>状态:</strong> {getStatusTag(selectedVersion.status)}</p>
            <p><strong>创建时间:</strong> {new Date(selectedVersion.created_at).toLocaleString()}</p>

            {selectedVersion.content_summary && (
              <>
                <Divider>内容摘要</Divider>
                <p><strong>执行摘要:</strong></p>
                <div style={{
                  background: '#f5f5f5',
                  padding: '12px',
                  borderRadius: '4px',
                  marginTop: '8px'
                }}>
                  {selectedVersion.content_summary.executive_summary}
                </div>

                <p style={{ marginTop: '12px' }}><strong>方案概述:</strong></p>
                <div style={{
                  background: '#f5f5f5',
                  padding: '12px',
                  borderRadius: '4px',
                  marginTop: '8px'
                }}>
                  {selectedVersion.content_summary.solution_overview}
                </div>
              </>
            )}
          </div>
        )}
      </Modal>

      {/* 迭代反馈弹窗 */}
      <Modal
        title="方案迭代"
        open={iterationModalVisible}
        onOk={handleIterate}
        onCancel={() => {
          setIterationModalVisible(false)
          setIterationFeedback('')
        }}
        width={600}
      >
        <Space direction="vertical" style={{ width: '100%' }}>
          <div>
            <p><strong>当前版本:</strong> v{selectedVersion?.version_number} - {selectedVersion?.title}</p>
            <p><strong>当前模型:</strong> {selectedVersion?.model_provider} - {selectedVersion?.model_name}</p>
          </div>

          <Form.Item label="选择生成模型" required>
            <Select
              mode="multiple"
              placeholder="选择用于迭代的AI模型"
              value={iterationModel}
              onChange={setIterationModel}
              style={{ width: '100%' }}
            >
              {models.map(model => (
                <Option key={model.provider} value={model.provider}>
                  {model.name}
                </Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item label="迭代反馈" required>
            <TextArea
              rows={6}
              placeholder="请详细描述对当前版本的意见和建议，以及希望改进的方向..."
              value={iterationFeedback}
              onChange={(e) => setIterationFeedback(e.target.value)}
            />
          </Form.Item>
        </Space>
      </Modal>

      {/* 版本对比弹窗 */}
      <Modal
        title="版本对比"
        open={comparisonModalVisible}
        onCancel={() => {
          setComparisonModalVisible(false)
          setCompareVersions([])
        }}
        onOk={handleCompare}
        width={1000}
      >
        <div>
          <p><strong>选择对比版本 ({compareVersions.length})</strong></p>
          <Select
            mode="multiple"
            placeholder="选择要对比的版本"
            value={compareVersions.map(v => v.id)}
            onChange={(values) => {
              setCompareVersions(
                compareVersions.filter(v => values.includes(v.id))
              )
            }}
            style={{ width: '100%', marginBottom: 16 }}
          >
            {versions.map(version => (
              <Option key={version.id} value={version.id}>
                v{version.version_number} - {version.title}
              </Option>
            ))}
          </Select>
        </div>
      </Modal>
    </div>
  )
}

export default MultiModelProposalGenerator