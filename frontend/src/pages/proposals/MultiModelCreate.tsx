import React, { useState, useEffect } from 'react'
import {
  Card,
  Form,
  Input,
  Select,
  Button,
  Steps,
  Row,
  Col,
  Alert,
  Spin,
  message,
  Space,
  Radio,
  Tabs,
  Divider,
  Tag,
  Progress,
  Result,
  Modal,
  List,
  Typography
} from 'antd'
import {
  RobotOutlined,
  SettingOutlined,
  PlayCircleOutlined,
  CompareArrowsOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  EyeOutlined
} from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import multiModelProposalService from '../../services/multiModelProposalService'
import {
  MultiModelProposalCreate,
  ModelSelectionResponse,
  MultiModelProposalResponse,
  PreviewResponse,
  ComparisonResponse
} from '../../services/multiModelProposalService'

const { TextArea } = Input
const { Step } = Steps
const { Option } = Select
const { TabPane } = Tabs
const { Title, Text } = Typography

const MultiModelCreate: React.FC = () => {
  const navigate = useNavigate()
  const [currentStep, setCurrentStep] = useState(0)
  const [availableModels, setAvailableModels] = useState<ModelSelectionResponse[]>([])
  const [defaultModel, setDefaultModel] = useState<ModelSelectionResponse | null>(null)
  const [selectedModel, setSelectedModel] = useState<ModelSelectionResponse | null>(null)
  const [comparisonModels, setComparisonModels] = useState<number[]>([])
  const [loading, setLoading] = useState(false)
  const [generating, setGenerating] = useState(false)
  const [previewData, setPreviewData] = useState<PreviewResponse | null>(null)
  const [comparisonResult, setComparisonResult] = useState<ComparisonResponse | null>(null)
  const [proposalResult, setProposalResult] = useState<MultiModelProposalResponse | null>(null)
  const [form] = Form.useForm()
  const [activeTab, setActiveTab] = useState('single')

  // 加载可用模型
  useEffect(() => {
    loadModels()
  }, [])

  const loadModels = async () => {
    try {
      const [models, defaultM] = await Promise.all([
        multiModelProposalService.getAvailableModels(),
        multiModelProposalService.getDefaultModel().catch(() => null)
      ])
      setAvailableModels(models)
      setDefaultModel(defaultM)
      if (defaultM && !selectedModel) {
        setSelectedModel(defaultM)
      }
    } catch (error) {
      message.error('加载模型列表失败')
    }
  }

  // 单模型生成
  const handleSingleGenerate = async (preview = false) => {
    if (!selectedModel) {
      message.error('请选择一个模型')
      return
    }

    const values = await form.validateFields()
    const proposalData: MultiModelProposalCreate = {
      ...values,
      model_id: selectedModel.id
    }

    try {
      if (preview) {
        setLoading(true)
        const result = await multiModelProposalService.previewProposal(proposalData)
        setPreviewData(result)
        setLoading(false)
        Modal.info({
          title: '预览结果',
          width: 800,
          content: (
            <div>
              <Alert
                type="success"
                message={`使用 ${result.model_info.name} 生成的预览`}
                style={{ marginBottom: 16 }}
              />
              <Tabs>
                <TabPane tab="执行摘要" key="summary">
                  <div style={{ 
                    background: '#f5f5f5', 
                    padding: 12, 
                    borderRadius: 4,
                    maxHeight: 300,
                    overflow: 'auto'
                  }}>
                    {result.preview.executive_summary}
                  </div>
                </TabPane>
                <TabPane tab="解决方案" key="solution">
                  <div style={{ 
                    background: '#f5f5f5', 
                    padding: 12, 
                    borderRadius: 4,
                    maxHeight: 300,
                    overflow: 'auto'
                  }}>
                    {result.preview.solution_overview}
                  </div>
                </TabPane>
                <TabPane tab="技术细节" key="technical">
                  <div style={{ 
                    background: '#f5f5f5', 
                    padding: 12, 
                    borderRadius: 4,
                    maxHeight: 300,
                    overflow: 'auto'
                  }}>
                    {result.preview.technical_details}
                  </div>
                </TabPane>
              </Tabs>
            </div>
          ),
          okText: '关闭'
        })
      } else {
        setGenerating(true)
        const result = await multiModelProposalService.generateProposal(proposalData)
        setProposalResult(result)
        setGenerating(false)
        setCurrentStep(3)
        message.success('方案生成成功')
      }
    } catch (error: any) {
      setLoading(false)
      setGenerating(false)
      message.error(error.response?.data?.detail || '生成失败')
    }
  }

  // 多模型对比
  const handleComparison = async () => {
    if (comparisonModels.length < 2) {
      message.error('请至少选择2个模型进行对比')
      return
    }

    const values = await form.validateFields()
    
    try {
      setGenerating(true)
      const result = await multiModelProposalService.compareModels(
        { ...values, model_id: comparisonModels[0] },
        comparisonModels
      )
      setComparisonResult(result)
      setGenerating(false)
      setCurrentStep(3)
      message.success('模型对比完成')
    } catch (error: any) {
      setGenerating(false)
      message.error(error.response?.data?.detail || '对比失败')
    }
  }

  const steps = [
    {
      title: '基本信息',
      icon: <SettingOutlined />
    },
    {
      title: '模型选择',
      icon: <RobotOutlined />
    },
    {
      title: '生成方案',
      icon: <PlayCircleOutlined />
    },
    {
      title: '完成',
      icon: <CheckCircleOutlined />
    }
  ]

  const renderModelCard = (model: ModelSelectionResponse) => (
    <Card
      size="small"
      hoverable
      onClick={() => setSelectedModel(model)}
      style={{
        cursor: 'pointer',
        border: selectedModel?.id === model.id ? '2px solid #1890ff' : '1px solid #d9d9d9',
        marginBottom: 16
      }}
      actions={[
        <Button key="test" type="link" size="small">
          测试
        </Button>
      ]}
    >
      <Space direction="vertical" style={{ width: '100%' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
          <Title level={5} style={{ margin: 0 }}>{model.name}</Title>
          {defaultModel?.id === model.id && (
            <Tag color="gold">默认</Tag>
          )}
        </div>
        <Text type="secondary">{model.description}</Text>
        <Space>
          <Tag color="blue">{model.provider.toUpperCase()}</Tag>
          <Tag color="green">{model.model_name}</Tag>
        </Space>
        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
          <Text type="secondary">成功率</Text>
          <Text style={{ 
            color: model.success_rate > 90 ? '#52c41a' : 
                   model.success_rate > 70 ? '#faad14' : '#f5222d' 
          }}>
            {model.success_rate.toFixed(1)}%
          </Text>
        </div>
      </Space>
    </Card>
  )

  const renderComparisonResults = () => {
    if (!comparisonResult) return null

    return (
      <div>
        <Alert
          type="success"
          message={`对比完成 - ${comparisonResult.successful_models}/${comparisonResult.total_models} 个模型成功`}
          style={{ marginBottom: 24 }}
        />
        
        <Row gutter={[16, 16]}>
          {comparisonResult.comparisons.map((item, index) => (
            <Col span={12} key={index}>
              <Card
                title={
                  <Space>
                    {item.model.name}
                    {item.success ? (
                      <CheckCircleOutlined style={{ color: '#52c41a' }} />
                    ) : (
                      <ExclamationCircleOutlined style={{ color: '#f5222d' }} />
                    )}
                  </Space>
                }
                size="small"
              >
                {item.success ? (
                  <div>
                    <Tabs size="small">
                      <TabPane tab="摘要" key="summary">
                        <div style={{ maxHeight: 150, overflow: 'auto' }}>
                          {item.result?.executive_summary}
                        </div>
                      </TabPane>
                      <TabPane tab="方案" key="solution">
                        <div style={{ maxHeight: 150, overflow: 'auto' }}>
                          {item.result?.solution_overview}
                        </div>
                      </TabPane>
                    </Tabs>
                  </div>
                ) : (
                  <Alert
                    type="error"
                    message="生成失败"
                    description={item.error}
                  />
                )}
              </Card>
            </Col>
          ))}
        </Row>
      </div>
    )
  }

  return (
    <div style={{ padding: 24 }}>
      <Card>
        <Steps current={currentStep} items={steps} />
        
        <Divider />

        {currentStep === 0 && (
          <div>
            <Title level={4}>方案基本信息</Title>
            <Form
              form={form}
              layout="vertical"
              style={{ marginTop: 24 }}
            >
              <Row gutter={16}>
                <Col span={12}>
                  <Form.Item
                    label="方案标题"
                    name="title"
                    rules={[{ required: true, message: '请输入方案标题' }]}
                  >
                    <Input placeholder="请输入方案标题" />
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item
                    label="客户名称"
                    name="customer_name"
                    rules={[{ required: true, message: '请输入客户名称' }]}
                  >
                    <Input placeholder="请输入客户名称" />
                  </Form.Item>
                </Col>
              </Row>

              <Row gutter={16}>
                <Col span={8}>
                  <Form.Item
                    label="客户行业"
                    name="customer_industry"
                  >
                    <Select placeholder="请选择客户行业">
                      <Option value="banking">银行</Option>
                      <Option value="insurance">保险</Option>
                      <Option value="securities">证券</Option>
                      <Option value="fintech">金融科技</Option>
                    </Select>
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item
                    label="客户联系人"
                    name="customer_contact"
                  >
                    <Input placeholder="请输入联系人" />
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item
                    label="参考模板"
                    name="reference_template_id"
                  >
                    <Select placeholder="请选择模板">
                      <Option value={1}>银行风控方案模板</Option>
                      <Option value={2}>保险系统方案模板</Option>
                    </Select>
                  </Form.Item>
                </Col>
              </Row>

              <Form.Item
                label="需求描述"
                name="requirements"
                rules={[{ required: true, message: '请输入需求描述' }]}
              >
                <TextArea
                  rows={4}
                  placeholder="请详细描述方案需求，包括业务场景、技术要求、实施目标等"
                />
              </Form.Item>

              <Form.Item
                label="参考文档"
                name="reference_document_ids"
              >
                <Select
                  mode="multiple"
                  placeholder="请选择参考文档"
                  options={[
                    { label: '银行风控案例.pdf', value: 1 },
                    { label: '保险系统文档.docx', value: 2 },
                    { label: '金融行业报告.pdf', value: 3 }
                  ]}
                />
              </Form.Item>

              <div style={{ textAlign: 'right' }}>
                <Button type="primary" onClick={() => setCurrentStep(1)}>
                  下一步
                </Button>
              </div>
            </Form>
          </div>
        )}

        {currentStep === 1 && (
          <div>
            <Title level={4}>选择AI模型</Title>
            
            <Tabs activeKey={activeTab} onChange={setActiveTab}>
              <TabPane tab="单模型生成" key="single">
                <Row gutter={[16, 16]}>
                  {availableModels.map(model => (
                    <Col span={8} key={model.id}>
                      {renderModelCard(model)}
                    </Col>
                  ))}
                </Row>

                {selectedModel && (
                  <div style={{ marginTop: 24, textAlign: 'center' }}>
                    <Space>
                      <Button onClick={() => setCurrentStep(0)}>
                        上一步
                      </Button>
                      <Button onClick={() => handleSingleGenerate(true)}>
                        预览生成
                      </Button>
                      <Button type="primary" onClick={() => setCurrentStep(2)}>
                        下一步
                      </Button>
                    </Space>
                  </div>
                )}
              </TabPane>

              <TabPane tab="多模型对比" key="compare">
                <Alert
                  message="选择多个模型进行对比，最多可选3个模型"
                  type="info"
                  style={{ marginBottom: 16 }}
                />
                
                <Row gutter={[16, 16]}>
                  {availableModels.map(model => (
                    <Col span={8} key={model.id}>
                      <Card
                        size="small"
                        hoverable
                        style={{
                          cursor: 'pointer',
                          border: comparisonModels.includes(model.id) ? '2px solid #1890ff' : '1px solid #d9d9d9',
                          marginBottom: 16
                        }}
                        onClick={() => {
                          if (comparisonModels.includes(model.id)) {
                            setComparisonModels(comparisonModels.filter(id => id !== model.id))
                          } else if (comparisonModels.length < 3) {
                            setComparisonModels([...comparisonModels, model.id])
                          } else {
                            message.warning('最多选择3个模型')
                          }
                        }}
                      >
                        <Space direction="vertical" style={{ width: '100%' }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                            <Title level={5} style={{ margin: 0 }}>{model.name}</Title>
                            {comparisonModels.includes(model.id) && (
                              <CheckCircleOutlined style={{ color: '#1890ff' }} />
                            )}
                          </div>
                          <Space>
                            <Tag color="blue">{model.provider.toUpperCase()}</Tag>
                            <Tag color="green">{model.model_name}</Tag>
                          </Space>
                        </Space>
                      </Card>
                    </Col>
                  ))}
                </Row>

                {comparisonModels.length >= 2 && (
                  <div style={{ marginTop: 24, textAlign: 'center' }}>
                    <Space>
                      <Button onClick={() => setCurrentStep(0)}>
                        上一步
                      </Button>
                      <Button type="primary" onClick={() => setCurrentStep(2)}>
                        下一步
                      </Button>
                    </Space>
                  </div>
                )}
              </TabPane>
            </Tabs>
          </div>
        )}

        {currentStep === 2 && (
          <div>
            <Title level={4}>生成方案</Title>
            
            <div style={{ textAlign: 'center', padding: 40 }}>
              {activeTab === 'single' ? (
                <div>
                  <Title level={4}>使用 {selectedModel?.name} 生成方案</Title>
                  <Text type="secondary">点击开始生成按钮，AI将根据您的需求生成完整的售前方案</Text>
                  
                  <div style={{ marginTop: 32 }}>
                    <Space>
                      <Button onClick={() => setCurrentStep(1)}>
                        上一步
                      </Button>
                      <Button 
                        type="primary" 
                        icon={<PlayCircleOutlined />}
                        loading={generating}
                        onClick={() => handleSingleGenerate(false)}
                      >
                        {generating ? '生成中...' : '开始生成'}
                      </Button>
                    </Space>
                  </div>
                </div>
              ) : (
                <div>
                  <Title level={4}>对比 {comparisonModels.length} 个模型</Title>
                  <Text type="secondary">将使用选中的模型同时生成方案，方便对比效果</Text>
                  
                  <div style={{ marginTop: 32 }}>
                    <Space>
                      <Button onClick={() => setCurrentStep(1)}>
                        上一步
                      </Button>
                      <Button 
                        type="primary" 
                        icon={<CompareArrowsOutlined />}
                        loading={generating}
                        onClick={handleComparison}
                      >
                        {generating ? '对比中...' : '开始对比'}
                      </Button>
                    </Space>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {currentStep === 3 && (
          <div>
            <Title level={4}>生成完成</Title>
            
            {proposalResult ? (
              <Result
                status="success"
                title="方案生成成功"
                subTitle={`使用 ${selectedModel?.name} 成功生成方案：${proposalResult.title}`}
                extra={[
                  <Button key="view" type="primary" onClick={() => {
                    navigate(`/proposals/${proposalResult.id}`)
                  }}>
                    查看方案
                  </Button>,
                  <Button key="new" onClick={() => {
                    window.location.reload()
                  }}>
                    生成新方案
                  </Button>
                ]}
              />
            ) : comparisonResult ? (
              renderComparisonResults()
            ) : null}
          </div>
        )}

        {loading && (
          <div style={{ 
            position: 'fixed', 
            top: 0, 
            left: 0, 
            right: 0, 
            bottom: 0, 
            background: 'rgba(255,255,255,0.8)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000
          }}>
            <Spin size="large" tip="生成预览中..." />
          </div>
        )}
      </Card>
    </div>
  )
}

export default MultiModelCreate
