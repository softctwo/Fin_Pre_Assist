import React, { useState, useEffect } from 'react'
import {
  Card,
  Form,
  Input,
  Select,
  InputNumber,
  Switch,
  Button,
  Table,
  Modal,
  message,
  Tabs,
  Space,
  Tag,
  Divider,
  Row,
  Col,
  Tooltip,
  Popconfirm,
  Alert
} from 'antd'
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  TestOutlined,
  SettingOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  ImportOutlined
} from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import aiModelService from '../../services/aiModelService'
import { AIModelConfig, CreateAIModelConfig, UpdateAIModelConfig } from '../../services/aiModelService'

const { TextArea } = Input
const { TabPane } = Tabs
const { Option } = Select

const ModelConfig: React.FC = () => {
  const navigate = useNavigate()
  const [models, setModels] = useState<AIModelConfig[]>([])
  const [loading, setLoading] = useState(false)
  const [modalVisible, setModalVisible] = useState(false)
  const [presetModalVisible, setPresetModalVisible] = useState(false)
  const [editingModel, setEditingModel] = useState<AIModelConfig | null>(null)
  const [testModalVisible, setTestModalVisible] = useState(false)
  const [testingModel, setTestingModel] = useState<AIModelConfig | null>(null)
  const [testResult, setTestResult] = useState<any>(null)
  const [testLoading, setTestLoading] = useState(false)
  const [presetModels, setPresetModels] = useState<any[]>([])
  const [form] = Form.useForm()
  const [activeTab, setActiveTab] = useState('models')

  // 加载模型列表
  const loadModels = async () => {
    setLoading(true)
    try {
      const response = await aiModelService.getModels()
      setModels(response.data)
    } catch (error) {
      message.error('加载模型列表失败')
    } finally {
      setLoading(false)
    }
  }

  // 加载预设模型
  const loadPresetModels = async () => {
    try {
      const presets = await aiModelService.getPresetModels()
      setPresetModels(presets)
    } catch (error) {
      message.error('加载预设模型失败')
    }
  }

  useEffect(() => {
    loadModels()
    loadPresetModels()
  }, [])

  // 创建或更新模型
  const handleSubmit = async (values: any) => {
    try {
      if (editingModel) {
        await aiModelService.updateModel(editingModel.id, values as UpdateAIModelConfig)
        message.success('模型配置更新成功')
      } else {
        await aiModelService.createModel(values as CreateAIModelConfig)
        message.success('模型配置创建成功')
      }
      setModalVisible(false)
      setEditingModel(null)
      form.resetFields()
      loadModels()
    } catch (error: any) {
      message.error(error.response?.data?.detail || '操作失败')
    }
  }

  // 删除模型
  const handleDelete = async (id: number) => {
    try {
      await aiModelService.deleteModel(id)
      message.success('模型配置删除成功')
      loadModels()
    } catch (error) {
      message.error('删除失败')
    }
  }

  // 测试模型
  const handleTest = async (model: AIModelConfig) => {
    setTestingModel(model)
    setTestResult(null)
    setTestModalVisible(true)
    setTestLoading(true)
    try {
      const result = await aiModelService.testModel(model.id)
      setTestResult(result)
      if (result.success) {
        message.success('模型测试成功')
      } else {
        message.error('模型测试失败')
      }
    } catch (error) {
      setTestResult({
        success: false,
        error: '测试请求失败'
      })
      message.error('测试请求失败')
    } finally {
      setTestLoading(false)
    }
  }

  // 设置默认模型
  const handleSetDefault = async (id: number) => {
    try {
      await aiModelService.setDefaultModel(id)
      message.success('已设置为默认模型')
      loadModels()
    } catch (error) {
      message.error('设置失败')
    }
  }

  // 导入预设模型
  const handleImportPreset = async (preset: any) => {
    try {
      await aiModelService.importPresetModel(preset.name)
      message.success('预设模型导入成功')
      loadModels()
    } catch (error: any) {
      message.error(error.response?.data?.detail || '导入失败')
    }
  }

  // 打开编辑弹窗
  const openEditModal = (model?: AIModelConfig) => {
    setEditingModel(model || null)
    if (model) {
      form.setFieldsValue(model)
    } else {
      form.resetFields()
    }
    setModalVisible(true)
  }

  const columns = [
    {
      title: '模型名称',
      dataIndex: 'name',
      key: 'name',
      render: (text: string, record: AIModelConfig) => (
        <Space>
          <span>{text}</span>
          {record.is_default && <Tag color="gold">默认</Tag>}
          {record.is_enabled && <Tag color="green">启用</Tag>}
          {!record.is_enabled && <Tag color="red">禁用</Tag>}
        </Space>
      )
    },
    {
      title: '供应商',
      dataIndex: 'provider',
      key: 'provider',
      render: (text: string) => (
        <Tag color="blue">{text.toUpperCase()}</Tag>
      )
    },
    {
      title: '模型',
      dataIndex: 'model_name',
      key: 'model_name'
    },
    {
      title: '成功率',
      dataIndex: 'success_rate',
      key: 'success_rate',
      render: (rate: number) => (
        <span style={{ color: rate > 90 ? '#52c41a' : rate > 70 ? '#faad14' : '#f5222d' }}>
          {rate.toFixed(1)}%
        </span>
      )
    },
    {
      title: '调用次数',
      dataIndex: 'total_calls',
      key: 'total_calls'
    },
    {
      title: '操作',
      key: 'actions',
      render: (text: any, record: AIModelConfig) => (
        <Space>
          <Tooltip title="测试模型">
            <Button
              type="link"
              icon={<TestOutlined />}
              onClick={() => handleTest(record)}
            />
          </Tooltip>
          <Tooltip title="编辑配置">
            <Button
              type="link"
              icon={<EditOutlined />}
              onClick={() => openEditModal(record)}
            />
          </Tooltip>
          {!record.is_default && (
            <Tooltip title="设为默认">
              <Button
                type="link"
                icon={<CheckCircleOutlined />}
                onClick={() => handleSetDefault(record.id)}
              />
            </Tooltip>
          )}
          <Popconfirm
            title="确定要删除这个模型配置吗？"
            onConfirm={() => handleDelete(record.id)}
          >
            <Tooltip title="删除">
              <Button
                type="link"
                danger
                icon={<DeleteOutlined />}
              />
            </Tooltip>
          </Popconfirm>
        </Space>
      )
    }
  ]

  return (
    <div style={{ padding: 24 }}>
      <Card
        title={
          <Space>
            <SettingOutlined />
            <span>AI模型配置</span>
          </Space>
        }
        extra={
          <Space>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={() => openEditModal()}
            >
              添加模型
            </Button>
          </Space>
        }
      >
        <Tabs activeKey={activeTab} onChange={setActiveTab}>
          <TabPane tab="模型配置" key="models">
            <Table
              columns={columns}
              dataSource={models}
              loading={loading}
              rowKey="id"
              pagination={{
                showSizeChanger: true,
                showQuickJumper: true,
                showTotal: (total) => `共 ${total} 条记录`
              }}
            />
          </TabPane>
          <TabPane tab="预设模型" key="presets">
            <Row gutter={[16, 16]}>
              {presetModels.map((preset, index) => (
                <Col span={8} key={index}>
                  <Card
                    size="small"
                    title={preset.name}
                    extra={
                      <Button
                        type="link"
                        icon={<ImportOutlined />}
                        onClick={() => handleImportPreset(preset)}
                      >
                        导入
                      </Button>
                    }
                  >
                    <div>
                      <p><strong>供应商:</strong> {preset.provider}</p>
                      <p><strong>模型:</strong> {preset.model_name}</p>
                      <p><strong>描述:</strong> {preset.description}</p>
                    </div>
                  </Card>
                </Col>
              ))}
            </Row>
          </TabPane>
        </Tabs>
      </Card>

      {/* 模型配置弹窗 */}
      <Modal
        title={editingModel ? '编辑模型配置' : '添加模型配置'}
        open={modalVisible}
        onCancel={() => {
          setModalVisible(false)
          setEditingModel(null)
          form.resetFields()
        }}
        footer={null}
        width={800}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
        >
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                label="模型名称"
                name="name"
                rules={[{ required: true, message: '请输入模型名称' }]}
              >
                <Input placeholder="例如: GPT-4" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                label="供应商"
                name="provider"
                rules={[{ required: true, message: '请选择供应商' }]}
              >
                <Select placeholder="选择供应商">
                  <Option value="openai">OpenAI</Option>
                  <Option value="tongyi">通义千问</Option>
                  <Option value="wenxin">文心一言</Option>
                  <Option value="zhipu">智谱AI</Option>
                  <Option value="deepseek">DeepSeek</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                label="模型名称"
                name="model_name"
                rules={[{ required: true, message: '请输入模型名称' }]}
              >
                <Input placeholder="例如: gpt-4" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                label="API基础URL"
                name="base_url"
              >
                <Input placeholder="可选，覆盖默认URL" />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item
            label="API密钥"
            name="api_key"
          >
            <Input.Password placeholder="请输入API密钥" />
          </Form.Item>

          <Row gutter={16}>
            <Col span={8}>
              <Form.Item
                label="最大输出Token"
                name="max_tokens"
                initialValue={2000}
              >
                <InputNumber min={1} max={32000} />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                label="上下文长度"
                name="context_length"
                initialValue={4096}
              >
                <InputNumber min={1} max={200000} />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                label="温度"
                name="temperature"
                initialValue={0.7}
              >
                <InputNumber min={0} max={2} step={0.1} />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={8}>
              <Form.Item
                label="Top-P"
                name="top_p"
                initialValue={1.0}
              >
                <InputNumber min={0} max={1} step={0.1} />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                label="频率惩罚"
                name="frequency_penalty"
                initialValue={0.0}
              >
                <InputNumber min={-2} max={2} step={0.1} />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                label="存在惩罚"
                name="presence_penalty"
                initialValue={0.0}
              >
                <InputNumber min={-2} max={2} step={0.1} />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                label="超时时间(秒)"
                name="timeout"
                initialValue={120}
              >
                <InputNumber min={10} max={600} />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                label="最大重试次数"
                name="max_retries"
                initialValue={3}
              >
                <InputNumber min={0} max={10} />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item
            label="描述"
            name="description"
          >
            <TextArea rows={3} placeholder="请输入模型描述" />
          </Form.Item>

          <Divider />

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                label="是否启用"
                name="is_enabled"
                valuePropName="checked"
                initialValue={true}
              >
                <Switch />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                label="设为默认"
                name="is_default"
                valuePropName="checked"
                initialValue={false}
              >
                <Switch />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item style={{ textAlign: 'right', marginBottom: 0 }}>
            <Space>
              <Button onClick={() => {
                setModalVisible(false)
                setEditingModel(null)
                form.resetFields()
              }}>
                取消
              </Button>
              <Button type="primary" htmlType="submit">
                {editingModel ? '更新' : '创建'}
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      {/* 测试结果弹窗 */}
      <Modal
        title={`测试模型 - ${testingModel?.name}`}
        open={testModalVisible}
        onCancel={() => setTestModalVisible(false)}
        footer={[
          <Button key="close" onClick={() => setTestModalVisible(false)}>
            关闭
          </Button>
        ]}
        width={700}
      >
        {testResult && (
          <div>
            <Alert
              type={testResult.success ? 'success' : 'error'}
              message={testResult.success ? '测试成功' : '测试失败'}
              description={testResult.success ? 
                `响应时间: ${testResult.duration_ms}ms` : 
                testResult.error
              }
              showIcon
              style={{ marginBottom: 16 }}
            />
            
            {testResult.success && testResult.response && (
              <div>
                <h4>模型响应:</h4>
                <div style={{ 
                  background: '#f5f5f5', 
                  padding: 12, 
                  borderRadius: 4,
                  whiteSpace: 'pre-wrap',
                  maxHeight: 300,
                  overflow: 'auto'
                }}>
                  {testResult.response}
                </div>
                
                {testResult.tokens_used && (
                  <p style={{ marginTop: 8 }}>
                    <strong>Token消耗:</strong> {testResult.tokens_used}
                  </p>
                )}
              </div>
            )}
          </div>
        )}
        
        {testLoading && (
          <div style={{ textAlign: 'center', padding: 40 }}>
            <div>正在测试模型连接...</div>
          </div>
        )}
      </Modal>
    </div>
  )
}

export default ModelConfig
