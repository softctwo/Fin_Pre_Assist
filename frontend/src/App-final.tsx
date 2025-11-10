import React, { useState, useEffect } from "react";
import { BrowserRouter as Router, Routes, Route, Navigate, Link, useNavigate } from 'react-router-dom'
import { ConfigProvider, Button, Card, Form, Input, Layout, Menu, Avatar, Space, message, Table, Tag, Spin, Modal, Select, Divider, List, Statistic, Row, Col, Upload, Tabs, UploadProps, Switch, InputNumber, DatePicker, Tree, Progress, Typography, Alert, Breadcrumb, Dropdown, Menu as AntdMenu } from 'antd'
import zhCN from 'antd/locale/zh_CN'
import ProposalDetailSimple from './pages/ProposalDetailSimple'
import {
  UserOutlined,
  LogoutOutlined,
  DashboardOutlined,
  FileTextOutlined,
  SettingOutlined,
  RobotOutlined,
  PlusOutlined,
  EyeOutlined,
  EditOutlined,
  DeleteOutlined,
  DownloadOutlined,
  HistoryOutlined,
  CalendarOutlined,
  TeamOutlined,
  CheckCircleOutlined,
  SyncOutlined,
  UploadOutlined,
  FolderOpenOutlined,
  FileOutlined,
  SearchOutlined,
  FilterOutlined,
  SettingFilled,
  ApiOutlined,
  DatabaseOutlined,
  CloudOutlined,
  SecurityScanOutlined,
  GlobalOutlined,
  TranslationOutlined,
  BulbOutlined,
  ThunderboltOutlined,
  ExperimentOutlined,
  AreaChartOutlined,
  BarChartOutlined,
  PieChartOutlined,
  RadarChartOutlined,
  InboxOutlined
} from '@ant-design/icons'

const { Header, Sider, Content } = Layout;
const { Option } = Select;
const { TextArea } = Input;
const { TabPane } = Tabs;
const { Title, Text } = Typography;
const { Search } = Input;
const { Dragger } = Upload;

// 简化的登录组件
const Login = () => {
  const [loading, setLoading] = useState(false);

  const onFinish = async (values: any) => {
    setLoading(true);
    try {
      const formData = new URLSearchParams();
      formData.append('username', values.username);
      formData.append('password', values.password);

      const response = await fetch('/api/v1/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData
      });

      if (response.ok) {
        const data = await response.json();
        localStorage.setItem('auth_token', data.access_token);
        localStorage.setItem('user_info', JSON.stringify({
          id: 1,
          username: values.username,
          email: '',
          full_name: '',
          role: 'admin'
        }));
        message.success('登录成功！');
        window.location.href = '/dashboard';
      } else {
        const errorData = await response.json();
        message.error(errorData.detail || '登录失败');
      }
    } catch (error: any) {
      console.error('登录失败:', error);
      message.error('登录失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      minHeight: '100vh',
      backgroundColor: '#f0f2f5',
      backgroundImage: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
    }}>
      <Card title="金融售前方案辅助系统" style={{ width: 420 }}>
        <Form onFinish={onFinish} layout="vertical" size="large">
          <Form.Item
            label="用户名"
            name="username"
            rules={[{ required: true, message: '请输入用户名' }]}
            initialValue="admin"
          >
            <Input prefix={<UserOutlined />} placeholder="请输入用户名" />
          </Form.Item>

          <Form.Item
            label="密码"
            name="password"
            rules={[{ required: true, message: '请输入密码' }]}
            initialValue="admin123"
          >
            <Input.Password prefix={<UserOutlined />} placeholder="请输入密码" />
          </Form.Item>

          <Form.Item>
            <Button type="primary" htmlType="submit" loading={loading} block style={{ height: 40, fontSize: 16 }}>
              {loading ? '登录中...' : '登录'}
            </Button>
          </Form.Item>
        </Form>

        <div style={{ marginTop: 24, padding: 16, backgroundColor: '#f8f9fa', borderRadius: 8, fontSize: 12, color: '#666' }}>
          <p style={{ margin: 0, fontWeight: 'bold', marginBottom: 8 }}>测试账户：</p>
          <p style={{ margin: '4px 0' }}>用户名: <code>admin</code></p>
          <p style={{ margin: '4px 0' }}>密码: <code>admin123</code></p>
        </div>
      </Card>
    </div>
  );
};

// 模板管理组件
const TemplateManagement = () => {
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingTemplate, setEditingTemplate] = useState(null);
  const [form] = Form.useForm();

  useEffect(() => {
    loadTemplates();
  }, []);

  const loadTemplates = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('auth_token');
      const response = await fetch('/api/v1/templates/', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setTemplates(data.items || data || []);
      } else {
        message.error('获取模板列表失败');
      }
    } catch (error) {
      console.error('获取模板失败:', error);
      message.error('获取模板列表失败');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateTemplate = () => {
    setEditingTemplate(null);
    form.resetFields();
    setModalVisible(true);
  };

  const handleEditTemplate = (template) => {
    setEditingTemplate(template);
    form.setFieldsValue(template);
    setModalVisible(true);
  };

  const handleSaveTemplate = async (values) => {
    try {
      const token = localStorage.getItem('auth_token');
      const url = editingTemplate
        ? `/api/v1/templates/${editingTemplate.id}`
        : '/api/v1/templates/';

      const response = await fetch(url, {
        method: editingTemplate ? 'PUT' : 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(values)
      });

      if (response.ok) {
        message.success(editingTemplate ? '模板更新成功' : '模板创建成功');
        setModalVisible(false);
        loadTemplates();
      } else {
        message.error('操作失败');
      }
    } catch (error) {
      console.error('保存模板失败:', error);
      message.error('操作失败');
    }
  };

  const handleDeleteTemplate = async (id) => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`/api/v1/templates/${id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        message.success('模板删除成功');
        loadTemplates();
      } else {
        message.error('删除失败');
      }
    } catch (error) {
      console.error('删除模板失败:', error);
      message.error('删除失败');
    }
  };

  const columns = [
    {
      title: '模板名称',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: '类型',
      dataIndex: 'type',
      key: 'type',
      render: (type) => (
        <Tag color={type === 'proposal' ? 'blue' : 'green'}>
          {type === 'proposal' ? '方案模板' : '文档模板'}
        </Tag>
      ),
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
    },
    {
      title: '操作',
      key: 'action',
      render: (_, record) => (
        <Space>
          <Button size="small" icon={<EditOutlined />} onClick={() => handleEditTemplate(record)}>
            编辑
          </Button>
          <Button size="small" icon={<DeleteOutlined />} danger onClick={() => handleDeleteTemplate(record.id)}>
            删除
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <h2>模板管理</h2>
        <Button type="primary" icon={<PlusOutlined />} onClick={handleCreateTemplate}>
          创建模板
        </Button>
      </div>

      <Card>
        <Table
          columns={columns}
          dataSource={templates}
          rowKey="id"
          loading={loading}
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 条记录`,
          }}
        />
      </Card>

      <Modal
        title={editingTemplate ? '编辑模板' : '创建模板'}
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={null}
        width={800}
      >
        <Form form={form} layout="vertical" onFinish={handleSaveTemplate}>
          <Form.Item
            label="模板名称"
            name="name"
            rules={[{ required: true, message: '请输入模板名称' }]}
          >
            <Input placeholder="请输入模板名称" />
          </Form.Item>

          <Form.Item
            label="模板类型"
            name="type"
            rules={[{ required: true, message: '请选择模板类型' }]}
          >
            <Select placeholder="请选择模板类型">
              <Option value="proposal">方案模板</Option>
              <Option value="document">文档模板</Option>
            </Select>
          </Form.Item>

          <Form.Item
            label="描述"
            name="description"
          >
            <Input.TextArea placeholder="请输入模板描述" rows={2} />
          </Form.Item>

          <Form.Item
            label="模板内容"
            name="content"
            rules={[{ required: true, message: '请输入模板内容' }]}
          >
            <Input.TextArea placeholder="请输入模板内容" rows={10} />
          </Form.Item>

          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                {editingTemplate ? '更新' : '创建'}
              </Button>
              <Button onClick={() => setModalVisible(false)}>
                取消
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

// 文档管理组件
const DocumentManagement = () => {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(false);
  const [uploadVisible, setUploadVisible] = useState(false);

  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('auth_token');

      if (!token) {
        message.error('请先登录');
        return;
      }

      const response = await fetch('/api/v1/documents/', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setDocuments(data.items || data || []);
        if (data.items && data.items.length > 0) {
          message.success(`成功加载 ${data.items.length} 个文档`);
        }
      } else {
        message.error('获取文档列表失败');
      }
    } catch (error) {
      console.error('获取文档失败:', error);
      message.error('获取文档列表失败');
    } finally {
      setLoading(false);
    }
  };

  const uploadProps: UploadProps = {
    name: 'file',
    multiple: true,
    action: '/api/v1/documents/upload',
    headers: {
      authorization: `Bearer ${localStorage.getItem('auth_token')}`,
    },
    onChange(info) {
      const { status } = info.file;
      if (status === 'done') {
        message.success(`${info.file.name} 文件上传成功`);
        loadDocuments();
      } else if (status === 'error') {
        message.error(`${info.file.name} 文件上传失败`);
      }
    },
  };

  const handlePreview = (record) => {
    // 在新窗口中打开文档预览
    window.open(`/api/v1/documents/${record.id}/preview`, '_blank');
  };

  const handleDownload = async (record) => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`/api/v1/documents/${record.id}/download`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = record.file_name;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        message.success('文档下载成功');
      } else {
        message.error('文档下载失败');
      }
    } catch (error) {
      console.error('下载文档失败:', error);
      message.error('文档下载失败');
    }
  };

  const handleDelete = async (record) => {
    Modal.confirm({
      title: '确认删除',
      content: `确定要删除文档 "${record.title}" 吗？`,
      okText: '确定',
      cancelText: '取消',
      okType: 'danger',
      onOk: async () => {
        try {
          const token = localStorage.getItem('auth_token');
          const response = await fetch(`/api/v1/documents/${record.id}`, {
            method: 'DELETE',
            headers: {
              'Authorization': `Bearer ${token}`
            }
          });

          if (response.ok) {
            message.success('文档删除成功');
            loadDocuments();
          } else {
            message.error('文档删除失败');
          }
        } catch (error) {
          console.error('删除文档失败:', error);
          message.error('文档删除失败');
        }
      }
    });
  };

  const columns = [
    {
      title: '文档标题',
      dataIndex: 'title',
      key: 'title',
    },
    {
      title: '文件名',
      dataIndex: 'file_name',
      key: 'file_name',
    },
    {
      title: '类型',
      dataIndex: 'type',
      key: 'type',
      render: (type) => (
        <Tag color={type === 'proposal' ? 'blue' : type === 'contract' ? 'green' : 'orange'}>
          {type === 'proposal' ? '方案' : type === 'contract' ? '合同' : '其他'}
        </Tag>
      ),
    },
    {
      title: '文件大小',
      dataIndex: 'file_size',
      key: 'file_size',
      render: (size) => size ? `${(size / 1024).toFixed(2)} KB` : '-',
    },
    {
      title: '上传时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (time) => new Date(time).toLocaleString(),
    },
    {
      title: '操作',
      key: 'action',
      render: (_, record) => (
        <Space>
          <Button
            size="small"
            icon={<EyeOutlined />}
            onClick={() => handlePreview(record)}
          >
            预览
          </Button>
          <Button
            size="small"
            icon={<DownloadOutlined />}
            onClick={() => handleDownload(record)}
          >
            下载
          </Button>
          <Button
            size="small"
            icon={<DeleteOutlined />}
            danger
            onClick={() => handleDelete(record)}
          >
            删除
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <h2>文档管理</h2>
        <Button type="primary" icon={<UploadOutlined />} onClick={() => setUploadVisible(true)}>
          上传文档
        </Button>
      </div>

      <Card>
        <Table
          columns={columns}
          dataSource={documents}
          rowKey="id"
          loading={loading}
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 条记录`,
          }}
        />
      </Card>

      <Modal
        title="上传文档"
        open={uploadVisible}
        onCancel={() => setUploadVisible(false)}
        footer={[
          <Button key="back" onClick={() => setUploadVisible(false)}>
            取消
          </Button>,
        ]}
      >
        <Dragger {...uploadProps}>
          <p className="ant-upload-drag-icon">
            <InboxOutlined />
          </p>
          <p className="ant-upload-text">点击或拖拽文件到此区域上传</p>
          <p className="ant-upload-hint">
            支持单个或批量上传。严格禁止上传公司数据或其他敏感文件。
          </p>
        </Dragger>
      </Modal>
    </div>
  );
};

// AI模型配置组件
const AIModelConfig = () => {
  const [models, setModels] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [editingModel, setEditingModel] = useState(null);
  const [form] = Form.useForm();
  const [testingModel, setTestingModel] = useState(null);
  const [showTestModal, setShowTestModal] = useState(false);

  useEffect(() => {
    loadModels();
  }, []);

  const loadModels = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('auth_token');
      const response = await fetch('/api/v1/ai/models', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setModels(data || []);
      } else {
        message.error('获取模型列表失败');
      }
    } catch (error) {
      console.error('获取模型失败:', error);
      message.error('获取模型列表失败');
    } finally {
      setLoading(false);
    }
  };

  const handleAddModel = () => {
    setEditingModel(null);
    form.resetFields();
    setShowModal(true);
  };

  const handleEditModel = (model) => {
    setEditingModel(model);
    form.setFieldsValue({
      name: model.name,
      provider: model.provider,
      model_name: model.model_name,
      api_key: '',
      base_url: model.base_url,
      max_tokens: model.max_tokens,
      context_length: model.context_length,
      temperature: model.temperature,
      top_p: model.top_p,
      timeout: model.timeout,
      max_retries: model.max_retries,
      description: model.description,
      is_enabled: model.is_enabled
    });
    setShowModal(true);
  };

  const handleSaveModel = async () => {
    try {
      const values = await form.validateFields();
      const token = localStorage.getItem('auth_token');

      const isEditing = editingModel !== null;
      const url = isEditing ? `/api/v1/ai/models/${editingModel.id}` : '/api/v1/ai/models';
      const method = isEditing ? 'PUT' : 'POST';

      const response = await fetch(url, {
        method: method,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(values)
      });

      if (response.ok) {
        const successMessage = isEditing ? '模型更新成功' : '模型添加成功';
        message.success(successMessage);
        setShowModal(false);
        form.resetFields();
        setEditingModel(null);
        loadModels();
      } else {
        const errorData = await response.json();
        const action = isEditing ? '更新' : '添加';
        message.error(`${action}模型失败: ${errorData.detail || '未知错误'}`);
      }
    } catch (error) {
      console.error('保存模型失败:', error);
      message.error('保存模型失败');
    }
  };

  const handleTestModel = async (model) => {
    setTestingModel(model);
    setShowTestModal(true);
  };

  const handleRunTest = async (values) => {
    if (!testingModel) return;

    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`/api/v1/ai/models/${testingModel.id}/test`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          prompt: values.prompt,
          temperature: values.temperature,
          max_tokens: values.max_tokens
        })
      });

      if (response.ok) {
        const result = await response.json();
        message.success(`测试成功，耗时: ${result.duration_ms}ms`);
        if (result.response) {
          Modal.info({
            title: '测试结果',
            content: (
              <div>
                <p><strong>响应:</strong></p>
                <div style={{
                  background: '#f5f5f5',
                  padding: '10px',
                  borderRadius: '4px',
                  maxHeight: '200px',
                  overflow: 'auto'
                }}>
                  {result.response}
                </div>
                {result.tokens_used && (
                  <p style={{ marginTop: '10px' }}>
                    <strong>Token使用:</strong> {result.tokens_used}
                  </p>
                )}
              </div>
            ),
            width: 600
          });
        }
      } else {
        const errorData = await response.json();
        message.error(`测试失败: ${errorData.detail || '未知错误'}`);
      }
    } catch (error) {
      console.error('测试模型失败:', error);
      message.error('测试模型失败');
    }
  };

  const handleDeleteModel = (model) => {
    Modal.confirm({
      title: '确认删除',
      content: `确定要删除模型 "${model.name}" 吗？`,
      okText: '确定',
      cancelText: '取消',
      okType: 'danger',
      onOk: async () => {
        try {
          const token = localStorage.getItem('auth_token');
          const response = await fetch(`/api/v1/ai/models/${model.id}`, {
            method: 'DELETE',
            headers: {
              'Authorization': `Bearer ${token}`
            }
          });

          if (response.ok) {
            message.success('模型删除成功');
            loadModels();
          } else {
            message.error('模型删除失败');
          }
        } catch (error) {
          console.error('删除模型失败:', error);
          message.error('模型删除失败');
        }
      }
    });
  };

  const columns = [
    {
      title: '模型名称',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: '供应商',
      dataIndex: 'provider',
      key: 'provider',
    },
    {
      title: '模型标识',
      dataIndex: 'model_name',
      key: 'model_name',
    },
    {
      title: '状态',
      dataIndex: 'is_enabled',
      key: 'is_enabled',
      render: (enabled) => (
        <Tag color={enabled ? 'green' : 'red'}>
          {enabled ? '启用' : '禁用'}
        </Tag>
      ),
    },
    {
      title: '默认',
      dataIndex: 'is_default',
      key: 'is_default',
      render: (isDefault) => (
        <Tag color={isDefault ? 'gold' : 'default'}>
          {isDefault ? '默认' : '普通'}
        </Tag>
      ),
    },
    {
      title: '成功率',
      dataIndex: 'success_rate',
      key: 'success_rate',
      render: (rate) => (
        <Progress
          percent={Math.round(rate || 0)}
          size="small"
          status={rate >= 90 ? 'success' : rate >= 70 ? 'normal' : 'exception'}
        />
      ),
    },
    {
      title: '总调用',
      dataIndex: 'total_calls',
      key: 'total_calls',
    },
    {
      title: '操作',
      key: 'action',
      render: (_, record) => (
        <Space>
          <Button
            size="small"
            icon={<ExperimentOutlined />}
            onClick={() => handleTestModel(record)}
          >
            测试
          </Button>
          <Button
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleEditModel(record)}
          >
            编辑
          </Button>
          <Button
            size="small"
            icon={<DeleteOutlined />}
            danger
            onClick={() => handleDeleteModel(record)}
          >
            删除
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <h2>AI模型配置</h2>
        <Button type="primary" icon={<PlusOutlined />} onClick={handleAddModel}>
          添加模型
        </Button>
      </div>

      <Alert
        message="AI模型配置"
        description="在这里配置和管理各种AI模型，包括Kimi、智谱AI、DeepSeek等。配置完成后可在多模型生成功能中使用。"
        type="info"
        showIcon
        style={{ marginBottom: 16 }}
      />

      <Card>
        <Table
          columns={columns}
          dataSource={models}
          rowKey="id"
          loading={loading}
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 条记录`,
          }}
        />
      </Card>

      {/* 添加/编辑模型模态框 */}
      <Modal
        title={editingModel ? '编辑模型' : '添加模型'}
        open={showModal}
        onOk={handleSaveModel}
        onCancel={() => {
          setShowModal(false);
          form.resetFields();
          setEditingModel(null);
        }}
        width={800}
      >
        <Form form={form} layout="vertical">
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                label="模型名称"
                name="name"
                rules={[{ required: true, message: '请输入模型名称' }]}
              >
                <Input placeholder="例如：Kimi Chat" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                label="供应商"
                name="provider"
                rules={[{ required: true, message: '请选择供应商' }]}
              >
                <Select placeholder="选择供应商">
                  <Option value="moonshot">Moonshot AI</Option>
                  <Option value="zhipuai">智谱AI</Option>
                  <Option value="deepseek">DeepSeek</Option>
                  <Option value="openai">OpenAI</Option>
                  <Option value="anthropic">Anthropic</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Form.Item
            label="模型标识"
            name="model_name"
            rules={[{ required: true, message: '请输入模型标识' }]}
          >
            <Input placeholder="例如：moonshot-v1-8k" />
          </Form.Item>

          <Form.Item
            label="API密钥"
            name="api_key"
          >
            <Input.Password placeholder="请输入API密钥（可选）" />
          </Form.Item>

          <Form.Item
            label="Base URL"
            name="base_url"
          >
            <Input placeholder="API基础URL（可选）" />
          </Form.Item>

          <Row gutter={16}>
            <Col span={8}>
              <Form.Item
                label="最大Token数"
                name="max_tokens"
              >
                <InputNumber min={1} max={100000} placeholder="2000" style={{ width: '100%' }} />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                label="上下文长度"
                name="context_length"
              >
                <InputNumber min={1} max={200000} placeholder="4096" style={{ width: '100%' }} />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                label="超时时间(秒)"
                name="timeout"
              >
                <InputNumber min={1} max={600} placeholder="120" style={{ width: '100%' }} />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={8}>
              <Form.Item
                label="Temperature"
                name="temperature"
              >
                <InputNumber min={0} max={2} step={0.1} placeholder="0.7" style={{ width: '100%' }} />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                label="Top P"
                name="top_p"
              >
                <InputNumber min={0} max={1} step={0.1} placeholder="1.0" style={{ width: '100%' }} />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                label="重试次数"
                name="max_retries"
              >
                <InputNumber min={0} max={10} placeholder="3" style={{ width: '100%' }} />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item
            label="描述"
            name="description"
          >
            <TextArea rows={3} placeholder="模型描述（可选）" />
          </Form.Item>

          <Form.Item
            name="is_enabled"
            valuePropName="checked"
          >
            <Switch checkedChildren="启用" unCheckedChildren="禁用" />
          </Form.Item>
        </Form>
      </Modal>

      {/* 测试模型模态框 */}
      <Modal
        title={`测试模型: ${testingModel?.name}`}
        open={showTestModal}
        onCancel={() => setShowTestModal(false)}
        footer={null}
        width={600}
      >
        <Form onFinish={handleRunTest} layout="vertical">
          <Form.Item
            label="测试提示"
            name="prompt"
            initialValue="请简单介绍一下你自己。"
            rules={[{ required: true, message: '请输入测试提示' }]}
          >
            <TextArea rows={3} />
          </Form.Item>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item label="Temperature">
                <InputNumber
                  min={0}
                  max={2}
                  step={0.1}
                  placeholder="0.7"
                  style={{ width: '100%' }}
                />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item label="最大Token">
                <InputNumber
                  min={1}
                  max={4000}
                  placeholder="500"
                  style={{ width: '100%' }}
                />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                运行测试
              </Button>
              <Button onClick={() => setShowTestModal(false)}>
                取消
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

// 系统设置组件
const SystemSettings = () => {
  const [settings, setSettings] = useState({
    theme: 'light',
    language: 'zh-CN',
    notifications: true,
    autoSave: true,
    apiTimeout: 30,
    maxRetries: 3,
  });

  return (
    <div>
      <h2>系统设置</h2>

      <Tabs defaultActiveKey="general" style={{ marginTop: 16 }}>
        <TabPane tab="通用设置" key="general">
          <Card title="界面设置">
            <Row gutter={[16, 16]}>
              <Col span={12}>
                <Form layout="vertical">
                  <Form.Item label="主题风格">
                    <Select value={settings.theme} onChange={(value) => setSettings({...settings, theme: value})}>
                      <Option value="light">浅色主题</Option>
                      <Option value="dark">深色主题</Option>
                      <Option value="auto">跟随系统</Option>
                    </Select>
                  </Form.Item>
                  <Form.Item label="语言设置">
                    <Select value={settings.language} onChange={(value) => setSettings({...settings, language: value})}>
                      <Option value="zh-CN">简体中文</Option>
                      <Option value="en-US">English</Option>
                    </Select>
                  </Form.Item>
                </Form>
              </Col>
              <Col span={12}>
                <Form layout="vertical">
                  <Form.Item label="通知设置">
                    <Space direction="vertical">
                      <Space>
                        <Switch checked={settings.notifications} onChange={(checked) => setSettings({...settings, notifications: checked})} />
                        <Text>启用桌面通知</Text>
                      </Space>
                      <Space>
                        <Switch checked={settings.autoSave} onChange={(checked) => setSettings({...settings, autoSave: checked})} />
                        <Text>自动保存草稿</Text>
                      </Space>
                    </Space>
                  </Form.Item>
                </Form>
              </Col>
            </Row>
          </Card>
        </TabPane>

        <TabPane tab="API设置" key="api">
          <Card title="API配置">
            <Form layout="vertical">
              <Row gutter={[16, 16]}>
                <Col span={12}>
                  <Form.Item label="请求超时时间（秒）">
                    <InputNumber
                      value={settings.apiTimeout}
                      onChange={(value) => setSettings({...settings, apiTimeout: value})}
                      min={10}
                      max={300}
                    />
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item label="最大重试次数">
                    <InputNumber
                      value={settings.maxRetries}
                      onChange={(value) => setSettings({...settings, maxRetries: value})}
                      min={1}
                      max={10}
                    />
                  </Form.Item>
                </Col>
              </Row>
            </Form>
          </Card>
        </TabPane>

        <TabPane tab="存储设置" key="storage">
          <Card title="存储配置">
            <Alert
              message="存储配置"
              description="配置文档存储路径、备份策略等存储相关设置。"
              type="info"
              showIcon
            />
            <div style={{ marginTop: 16 }}>
              <Space direction="vertical" style={{ width: '100%' }}>
                <div>
                  <Title level={5}>存储空间使用</Title>
                  <Progress percent={45} showInfo={{ format: (percent) => `${percent}% 已使用` }} />
                </div>
                <div>
                  <Title level={5}>备份设置</Title>
                  <Space>
                    <Switch defaultChecked />
                    <Text>自动备份</Text>
                  </Space>
                </div>
              </Space>
            </div>
          </Card>
        </TabPane>

        <TabPane tab="安全设置" key="security">
          <Card title="安全配置">
            <Space direction="vertical" style={{ width: '100%' }}>
              <Space>
                <Switch defaultChecked />
                <Text>启用双因素认证</Text>
              </Space>
              <Space>
                <Switch defaultChecked />
                <Text>会话超时自动登出</Text>
              </Space>
              <Space>
                <Switch />
                <Text>敏感操作二次确认</Text>
              </Space>
            </Space>
          </Card>
        </TabPane>
      </Tabs>
    </div>
  );
};

// 完整的仪表盘组件
const Dashboard = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('overview');
  const [models, setModels] = useState([]);
  const [loadingModels, setLoadingModels] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [results, setResults] = useState([]);
  const [selectedModels, setSelectedModels] = useState([]);
  const [proposals, setProposals] = useState([]);
  const [loadingProposals, setLoadingProposals] = useState(false);
  const [form] = Form.useForm();
  const [currentUser] = useState(JSON.parse(localStorage.getItem('user_info') || '{}'));

  // 新增方案管理相关状态
  const [showCreateProposalModal, setShowCreateProposalModal] = useState(false);
  const [showProposalDetailModal, setShowProposalDetailModal] = useState(false);
  const [showGenerateContentModal, setShowGenerateContentModal] = useState(false);
  const [editingProposal, setEditingProposal] = useState(null);
  const [viewingProposal, setViewingProposal] = useState(null);
  const [proposalForm, setProposalForm] = useState({
    title: '',
    clientName: '',
    industry: '',
    requirements: '',
    budgetRange: '',
    timeline: '',
    status: 'draft'
  });
  const [generateContentForm, setGenerateContentForm] = useState({
    selectedModels: ['moonshot-v1-8k'],
    comparisonMode: false,
  });
  const [loading, setLoading] = useState(false);
  const [generatingContent, setGeneratingContent] = useState(false);

  useEffect(() => {
    // 初始化时加载方案数据用于首页统计
    loadProposals();
    if (activeTab === 'multi-model') {
      loadModels();
    }
  }, [activeTab]);

  const loadModels = async () => {
    try {
      setLoadingModels(true);
      const token = localStorage.getItem('auth_token');
      const response = await fetch('/api/v1/multi-model-proposals/models/available', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setModels(data);
      } else {
        message.error('获取模型列表失败');
      }
    } catch (error) {
      console.error('获取模型失败:', error);
      message.error('获取模型列表失败');
    } finally {
      setLoadingModels(false);
    }
  };

  const loadProposals = async () => {
    try {
      setLoadingProposals(true);
      const token = localStorage.getItem('auth_token');
      const response = await fetch('/api/v1/proposals/', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setProposals(data.items || []);
      } else {
        message.error('获取方案列表失败');
      }
    } catch (error) {
      console.error('获取方案失败:', error);
      message.error('获取方案列表失败');
    } finally {
      setLoadingProposals(false);
    }
  };

  const handleGenerate = async () => {
    if (selectedModels.length === 0) {
      message.warning('请选择至少一个模型');
      return;
    }

    try {
      const values = await form.validateFields();
      setGenerating(true);
      setResults([]);

      const token = localStorage.getItem('auth_token');
      const promises = selectedModels.map(modelId =>
        fetch('/api/v1/multi-model-proposals/generate', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({
            ...values,
            model_id: modelId,
            customer_industry: values.customer_industry || 'banking'
          })
        })
      );

      const responses = await Promise.all(promises);
      const validResults = [];

      for (let i = 0; i < responses.length; i++) {
        const response = responses[i];
        if (response.ok) {
          const result = await response.json();
          validResults.push({
            id: result.id,
            model: models.find(m => m.id === selectedModels[i])?.name || `Model ${i + 1}`,
            title: result.title,
            status: result.status,
            executive_summary: result.executive_summary,
            solution_overview: result.solution_overview,
            full_content: result.full_content,
            created_at: result.created_at,
            success: true
          });
        } else {
          validResults.push({
            id: i,
            model: models.find(m => m.id === selectedModels[i])?.name || `Model ${i + 1}`,
            title: '生成失败',
            status: 'failed',
            executive_summary: '',
            solution_overview: '',
            full_content: '',
            created_at: new Date().toISOString(),
            success: false,
            error: '生成失败'
          });
        }
      }

      setResults(validResults);
      message.success(`方案生成完成！成功: ${validResults.filter(r => r.success).length}/${validResults.length}`);
    } catch (error) {
      console.error('生成失败:', error);
      message.error('生成失败: ' + (error.message || '未知错误'));
    } finally {
      setGenerating(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user_info');
    message.success('已退出登录');
    window.location.href = '/login';
  };

  const resultColumns = [
    {
      title: '模型',
      dataIndex: 'model',
      key: 'model',
    },
    {
      title: '方案标题',
      dataIndex: 'title',
      key: 'title',
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status) => (
        <Tag color={status === 'completed' ? 'green' : status === 'failed' ? 'red' : 'processing'}>
          {status === 'completed' ? '已完成' : status === 'failed' ? '失败' : '生成中'}
        </Tag>
      ),
    },
    {
      title: '操作',
      key: 'action',
      render: (_, record) => (
        <Space>
          <Button
            size="small"
            icon={<EyeOutlined />}
            onClick={() => {
              if (record.success) {
                Modal.info({
                  title: `${record.model} 生成方案`,
                  width: 800,
                  content: (
                    <div style={{ maxHeight: 400, overflow: 'auto' }}>
                      <p><strong>执行摘要:</strong></p>
                      <p>{record.executive_summary || '暂无内容'}</p>
                      <p><strong>解决方案:</strong></p>
                      <p>{record.solution_overview || '暂无内容'}</p>
                      <p><strong>完整内容:</strong></p>
                      <p>{record.full_content || '暂无内容'}</p>
                    </div>
                  ),
                });
              } else {
                message.error(record.error || '方案生成失败');
              }
            }}
          >
            查看
          </Button>
        </Space>
      ),
    },
  ];

  const proposalColumns = [
    {
      title: '方案标题',
      dataIndex: 'title',
      key: 'title',
    },
    {
      title: '客户名称',
      dataIndex: 'customer_name',
      key: 'customer_name',
    },
    {
      title: '行业',
      dataIndex: 'customer_industry',
      key: 'customer_industry',
      render: (industry) => industry ? industry : '-',
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status) => (
        <Tag color={
          status === 'completed' ? 'green' :
          status === 'generating' ? 'blue' :
          status === 'draft' ? 'orange' : 'default'
        }>
          {
            status === 'completed' ? '已完成' :
            status === 'generating' ? '生成中' :
            status === 'draft' ? '草稿' : status
          }
        </Tag>
      ),
    },
    {
      title: '预算范围',
      dataIndex: 'budget_range',
      key: 'budget_range',
      render: (budget) => budget ? budget : '-',
    },
    {
      title: '项目周期',
      dataIndex: 'timeline',
      key: 'timeline',
      render: (timeline) => timeline ? timeline : '-',
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (time) => new Date(time).toLocaleString(),
    },
    {
      title: '操作',
      key: 'action',
      render: (_, record) => (
        <Space>
          <Button
            size="small"
            icon={<EyeOutlined />}
            onClick={() => handleViewProposal(record)}
          >
            查看详情
          </Button>
          {record.status === 'draft' && (
            <Button
              size="small"
              icon={<EditOutlined />}
              onClick={() => handleEditProposal(record)}
            >
              编辑
            </Button>
          )}
          {record.status === 'draft' && (
            <Button
              size="small"
              type="primary"
              icon={<RobotOutlined />}
              onClick={() => handleGenerateContent(record)}
            >
              生成内容
            </Button>
          )}
          {(record.status === 'draft' || record.status === 'completed') && (
            <Button
              size="small"
              danger
              icon={<DeleteOutlined />}
              onClick={() => handleDeleteProposal(record)}
            >
              删除
            </Button>
          )}
          {record.status === 'completed' && (
            <Dropdown
              overlay={
                <Menu>
                  <Menu.Item
                    key="word"
                    icon={<DownloadOutlined />}
                    onClick={() => handleExport(record, 'word')}
                  >
                    导出Word
                  </Menu.Item>
                  <Menu.Item
                    key="pdf"
                    icon={<DownloadOutlined />}
                    onClick={() => handleExport(record, 'pdf')}
                  >
                    导出PDF
                  </Menu.Item>
                  <Menu.Item
                    key="excel"
                    icon={<DownloadOutlined />}
                    onClick={() => handleExport(record, 'excel')}
                  >
                    导出报价单
                  </Menu.Item>
                </Menu>
              }
            >
              <Button size="small" icon={<DownloadOutlined />}>
                导出
              </Button>
            </Dropdown>
          )}
        </Space>
      ),
    },
  ];

  // 新增方案管理相关函数
  const handleCreateProposal = () => {
    setEditingProposal(null);
    setProposalForm({
      title: '',
      clientName: '',
      industry: '',
      requirements: '',
      budgetRange: '',
      timeline: '',
      status: 'draft'
    });
    setShowCreateProposalModal(true);
  };

  const handleEditProposal = (proposal) => {
    setEditingProposal(proposal);
    setProposalForm({
      title: proposal.title,
      clientName: proposal.customer_name,
      industry: proposal.customer_industry,
      requirements: proposal.requirements,
      budgetRange: proposal.budget_range || '',
      timeline: proposal.timeline || '',
      status: proposal.status
    });
    setShowCreateProposalModal(true);
  };

  // 当编辑方案时更新表单字段值
  useEffect(() => {
    if (showCreateProposalModal && editingProposal) {
      form.setFieldsValue({
        title: editingProposal.title,
        clientName: editingProposal.customer_name,
        industry: editingProposal.customer_industry,
        requirements: editingProposal.requirements,
        budgetRange: editingProposal.budget_range || '',
        timeline: editingProposal.timeline || ''
      });
    } else if (showCreateProposalModal && !editingProposal) {
      form.resetFields();
    }
  }, [showCreateProposalModal, editingProposal, form]);

  const handleSaveProposal = async () => {
    try {
      const values = await form.validateFields();
      setLoading(true);
      const token = localStorage.getItem('auth_token');

      const isEditing = editingProposal !== null;
      const url = isEditing ? `/api/v1/proposals/${editingProposal.id}` : '/api/v1/proposals/';
      const method = isEditing ? 'PUT' : 'POST';

      const response = await fetch(url, {
        method: method,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          title: values.title,
          customer_name: values.clientName,
          customer_industry: values.industry,
          customer_contact: null,
          requirements: values.requirements,
          budget_range: values.budgetRange || null,
          timeline: values.timeline || null,
          reference_document_ids: null
        })
      });

      if (response.ok) {
        const successMessage = isEditing ? '方案更新成功' : '方案创建成功';
        message.success(successMessage);
        setShowCreateProposalModal(false);
        form.resetFields();
        setEditingProposal(null);
        loadProposals();
      } else {
        const errorData = await response.json();
        const action = isEditing ? '更新' : '创建';
        console.error(`${action}方案失败:`, errorData);
        message.error(`${action}方案失败: ${errorData.detail || '未知错误'}`);
      }
    } catch (error) {
      console.error('保存方案失败:', error);
      message.error('保存方案失败');
    } finally {
      setLoading(false);
    }
  };

  const handleViewProposal = (proposal) => {
    // 跳转到独立的方案详情页面
    navigate(`/proposal/${proposal.id}`);
  };

  const handleGenerateContent = (proposal) => {
    setEditingProposal(proposal);
    setGenerateContentForm({
      selectedModels: ['moonshot-v1-8k'],
      comparisonMode: false,
    });
    setShowGenerateContentModal(true);
  };

  const handleGenerateContentInDetail = async (proposal) => {
    try {
      setGeneratingContent(true);
      setEditingProposal(proposal);
      const token = localStorage.getItem('auth_token');

      // 更新方案状态为生成中
      await fetch(`/api/v1/proposals/${proposal.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ status: 'generating' })
      });

      // 更新本地状态
      setViewingProposal({ ...viewingProposal, status: 'generating' });

      const promises = generateContentForm.selectedModels.map(modelId =>
        fetch('/api/v1/multi-model-proposals/generate', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({
            title: proposal.title,
            customer_name: proposal.customer_name,
            customer_industry: proposal.customer_industry,
            requirements: proposal.requirements,
            budget_range: proposal.budget_range,
            timeline: proposal.timeline,
            model_id: modelId,
            proposal_id: proposal.id
          })
        })
      );

      const responses = await Promise.all(promises);
      let successCount = 0;

      for (const response of responses) {
        if (response.ok) {
          successCount++;
        }
      }

      if (successCount > 0) {
        // 更新方案状态为已完成
        const updateResponse = await fetch(`/api/v1/proposals/${proposal.id}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({
            status: 'completed',
            executive_summary: '方案内容已生成完成',
            full_content: '详细的方案内容已生成，请查看详情页面'
          })
        });

        if (updateResponse.ok) {
          const updatedProposal = await updateResponse.json();
          setViewingProposal(updatedProposal);
        }

        message.success(`内容生成完成！成功: ${successCount}/${responses.length}`);
        loadProposals();
      } else {
        // 更新方案状态为草稿
        await fetch(`/api/v1/proposals/${proposal.id}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({ status: 'draft' })
        });

        setViewingProposal({ ...viewingProposal, status: 'draft' });
        message.error('内容生成失败');
      }
    } catch (error) {
      console.error('生成内容失败:', error);
      message.error('生成内容失败');
      setViewingProposal({ ...viewingProposal, status: 'draft' });
    } finally {
      setGeneratingContent(false);
    }
  };

  const handleStartGeneration = async () => {
    if (!editingProposal) return;

    try {
      setGeneratingContent(true);
      const token = localStorage.getItem('auth_token');

      // 更新方案状态为生成中
      await fetch(`/api/v1/proposals/${editingProposal.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ status: 'generating' })
      });

      const promises = generateContentForm.selectedModels.map(modelId =>
        fetch('/api/v1/multi-model-proposals/generate', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({
            title: editingProposal.title,
            customer_name: editingProposal.customer_name,
            customer_industry: editingProposal.customer_industry,
            requirements: editingProposal.requirements,
            budget_range: editingProposal.budget_range,
            timeline: editingProposal.timeline,
            model_id: modelId,
            proposal_id: editingProposal.id
          })
        })
      );

      const responses = await Promise.all(promises);
      let successCount = 0;

      for (const response of responses) {
        if (response.ok) {
          successCount++;
        }
      }

      if (successCount > 0) {
        // 更新方案状态为已完成
        await fetch(`/api/v1/proposals/${editingProposal.id}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({
            status: 'completed',
            executive_summary: '方案内容已生成完成',
            full_content: '详细的方案内容已生成，请查看详情页面'
          })
        });

        message.success(`内容生成完成！成功: ${successCount}/${responses.length}`);
        setShowGenerateContentModal(false);
        loadProposals();
      } else {
        message.error('内容生成失败');
      }
    } catch (error) {
      console.error('生成内容失败:', error);
      message.error('生成内容失败');
    } finally {
      setGeneratingContent(false);
    }
  };

  // 删除方案
  const handleDeleteProposal = (proposal) => {
    Modal.confirm({
      title: '确认删除方案',
      content: `确定要删除方案"${proposal.title}"吗？此操作不可撤销。`,
      okText: '确定删除',
      okType: 'danger',
      cancelText: '取消',
      onOk: async () => {
        try {
          const token = localStorage.getItem('auth_token');
          const response = await fetch(`/api/v1/proposals/${proposal.id}`, {
            method: 'DELETE',
            headers: {
              'Authorization': `Bearer ${token}`
            }
          });

          if (response.ok) {
            message.success('方案删除成功');
            loadProposals(); // 重新加载方案列表
          } else {
            const errorData = await response.json();
            message.error(errorData.detail || '方案删除失败');
          }
        } catch (error) {
          console.error('删除方案失败:', error);
          message.error('删除方案失败');
        }
      }
    });
  };

  const handleExport = async (proposal, format) => {
    try {
      const token = localStorage.getItem('auth_token');
      let requestFormat = format;
      if (format === 'word') {
        requestFormat = 'docx';
      } else if (format === 'excel') {
        requestFormat = 'xlsx';
      }

      const response = await fetch(`/api/v1/proposals/${proposal.id}/export?format=${requestFormat}`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;

        // 设置正确的文件扩展名
        let filename = `${proposal.title}`;
        if (requestFormat === 'docx') {
          filename += '.docx';
        } else if (requestFormat === 'xlsx') {
          filename += '_报价单.xlsx';
        } else {
          filename += `.${requestFormat}`;
        }

        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        message.success(`${format.toUpperCase()}导出成功`);
      } else {
        const errorData = await response.json();
        message.error(errorData.detail || `${format.toUpperCase()}导出失败`);
      }
    } catch (error) {
      console.error('导出失败:', error);
      message.error('导出失败');
    }
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider theme="dark" width={250}>
        <div style={{
          height: 64,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: 'white',
          fontSize: 16,
          fontWeight: 'bold'
        }}>
          金融售前系统
        </div>
        <Menu theme="dark" mode="inline" selectedKeys={[activeTab]} onClick={({ key }) => setActiveTab(key)}>
          <Menu.Item key="overview" icon={<DashboardOutlined />}>
            仪表盘
          </Menu.Item>
          <Menu.Item key="multi-model" icon={<RobotOutlined />}>
            多模型生成
          </Menu.Item>
          <Menu.Item key="proposals" icon={<FileTextOutlined />}>
            方案管理
          </Menu.Item>
          <Menu.Item key="templates" icon={<FileOutlined />}>
            模板管理
          </Menu.Item>
          <Menu.Item key="documents" icon={<FolderOpenOutlined />}>
            文档管理
          </Menu.Item>
          <Menu.Item key="ai-models" icon={<ApiOutlined />}>
            AI模型配置
          </Menu.Item>
          <Menu.Item key="settings" icon={<SettingOutlined />}>
            系统设置
          </Menu.Item>
        </Menu>
      </Sider>

      <Layout>
        <Header style={{
          background: '#fff',
          padding: '0 24px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
        }}>
          <div style={{ fontSize: 18, fontWeight: 'bold' }}>
            金融售前方案辅助系统
          </div>
          <Space>
            <span>欢迎，{currentUser?.username || '用户'}</span>
            <Avatar icon={<UserOutlined />} />
            <Button onClick={handleLogout}>退出登录</Button>
          </Space>
        </Header>

        <Content style={{
          margin: '24px 16px',
          padding: 24,
          background: '#fff',
          borderRadius: 8,
          minHeight: 280
        }}>
          {activeTab === 'overview' && (
            <div>
              <Breadcrumb style={{ marginBottom: 16 }}>
                <Breadcrumb.Item>仪表盘</Breadcrumb.Item>
                <Breadcrumb.Item>系统概览</Breadcrumb.Item>
              </Breadcrumb>

              <h1>欢迎使用金融售前方案辅助系统</h1>

              {/* 统计概览 */}
              <Row gutter={16} style={{ marginTop: 30 }}>
                <Col span={6}>
                  <Card>
                    <Statistic
                      title="总方案数"
                      value={proposals.length}
                      prefix={<FileTextOutlined />}
                      valueStyle={{ color: '#1890ff' }}
                    />
                  </Card>
                </Col>
                <Col span={6}>
                  <Card>
                    <Statistic
                      title="已完成"
                      value={proposals.filter(p => p.status === 'completed').length}
                      prefix={<CheckCircleOutlined />}
                      valueStyle={{ color: '#52c41a' }}
                    />
                  </Card>
                </Col>
                <Col span={6}>
                  <Card>
                    <Statistic
                      title="生成中"
                      value={proposals.filter(p => p.status === 'generating').length}
                      prefix={<SyncOutlined spin />}
                      valueStyle={{ color: '#fa8c16' }}
                    />
                  </Card>
                </Col>
                <Col span={6}>
                  <Card>
                    <Statistic
                      title="草稿"
                      value={proposals.filter(p => p.status === 'draft').length}
                      prefix={<EditOutlined />}
                      valueStyle={{ color: '#722ed1' }}
                    />
                  </Card>
                </Col>
              </Row>

              {/* 最近方案 */}
              <Card title="最近方案" style={{ marginTop: 30 }}>
                <List
                  itemLayout="horizontal"
                  dataSource={proposals.slice(0, 5)}
                  renderItem={item => (
                    <List.Item
                      actions={[
                        <Button
                          type="link"
                          icon={<EyeOutlined />}
                          onClick={() => navigate(`/proposal/${item.id}`)}
                        >
                          查看
                        </Button>
                      ]}
                    >
                      <List.Item.Meta
                        avatar={<Avatar icon={<FileTextOutlined />} />}
                        title={item.title}
                        description={`客户: ${item.customer_name} | ${new Date(item.created_at).toLocaleString()}`}
                      />
                    </List.Item>
                  )}
                />
              </Card>

              {/* 快捷功能 */}
              <Row gutter={[16, 16]} style={{ marginTop: 30 }}>
                <Col span={6}>
                  <Card
                    hoverable
                    onClick={() => setActiveTab('multi-model')}
                    style={{ cursor: 'pointer' }}
                  >
                    <RobotOutlined style={{ fontSize: 32, color: '#1890ff', marginBottom: 16 }} />
                    <Title level={4}>多模型生成</Title>
                    <p>使用多个AI模型同时生成方案</p>
                  </Card>
                </Col>
                <Col span={6}>
                  <Card
                    hoverable
                    onClick={() => setActiveTab('proposals')}
                    style={{ cursor: 'pointer' }}
                  >
                    <FileTextOutlined style={{ fontSize: 32, color: '#52c41a', marginBottom: 16 }} />
                    <Title level={4}>方案管理</Title>
                    <p>管理和编辑已生成的方案</p>
                  </Card>
                </Col>
                <Col span={6}>
                  <Card
                    hoverable
                    onClick={() => setActiveTab('templates')}
                    style={{ cursor: 'pointer' }}
                  >
                    <FileOutlined style={{ fontSize: 32, color: '#fa8c16', marginBottom: 16 }} />
                    <Title level={4}>模板管理</Title>
                    <p>创建和管理方案模板</p>
                  </Card>
                </Col>
                <Col span={6}>
                  <Card
                    hoverable
                    onClick={() => setActiveTab('documents')}
                    style={{ cursor: 'pointer' }}
                  >
                    <FolderOpenOutlined style={{ fontSize: 32, color: '#722ed1', marginBottom: 16 }} />
                    <Title level={4}>文档管理</Title>
                    <p>上传和管理参考文档</p>
                  </Card>
                </Col>
              </Row>

              <div style={{ marginTop: 30, padding: 20, backgroundColor: '#f0f8ff', borderRadius: 8 }}>
                <h3>系统功能特性</h3>
                <Row gutter={[16, 16]}>
                  <Col span={8}>
                    <Space direction="vertical">
                      <div>
                        <ThunderboltOutlined style={{ color: '#1890ff' }} />
                        <strong> 多AI模型支持</strong>
                        <p>集成Kimi、智谱AI、DeepSeek等多种大模型</p>
                      </div>
                      <div>
                        <ExperimentOutlined style={{ color: '#52c41a' }} />
                        <strong> 同步生成对比</strong>
                        <p>同时使用多个模型生成方案，直观对比效果</p>
                      </div>
                    </Space>
                  </Col>
                  <Col span={8}>
                    <Space direction="vertical">
                      <div>
                        <AreaChartOutlined style={{ color: '#fa8c16' }} />
                        <strong> 迭代优化功能</strong>
                        <p>基于用户反馈持续改进方案质量</p>
                      </div>
                      <div>
                        <DatabaseOutlined style={{ color: '#722ed1' }} />
                        <strong> 版本管理</strong>
                        <p>完整的方案版本历史和管理</p>
                      </div>
                    </Space>
                  </Col>
                  <Col span={8}>
                    <Space direction="vertical">
                      <div>
                        <CloudOutlined style={{ color: '#eb2f96' }} />
                        <strong> 模板系统</strong>
                        <p>预定义方案模板，提高生成效率</p>
                      </div>
                      <div>
                        <SecurityScanOutlined style={{ color: '#13c2c2' }} />
                        <strong> 文档知识库</strong>
                        <p>语义搜索，智能推荐相关内容</p>
                      </div>
                    </Space>
                  </Col>
                </Row>
              </div>
            </div>
          )}

          {activeTab === 'multi-model' && (
            <div>
              <Breadcrumb style={{ marginBottom: 16 }}>
                <Breadcrumb.Item>仪表盘</Breadcrumb.Item>
                <Breadcrumb.Item>多模型生成</Breadcrumb.Item>
              </Breadcrumb>

              <h2>多模型方案生成</h2>

              {/* 方案生成表单 */}
              <Card title="生成方案" style={{ marginTop: 16 }}>
                <Form form={form} layout="vertical">
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
                    <Form.Item
                      label="方案标题"
                      name="title"
                      rules={[{ required: true, message: '请输入方案标题' }]}
                    >
                      <Input placeholder="请输入方案标题" />
                    </Form.Item>
                    <Form.Item
                      label="客户名称"
                      name="customer_name"
                      rules={[{ required: true, message: '请输入客户名称' }]}
                    >
                      <Input placeholder="请输入客户名称" />
                    </Form.Item>
                  </div>

                  <Form.Item
                    label="客户行业"
                    name="customer_industry"
                    initialValue="banking"
                  >
                    <Select placeholder="请选择客户行业">
                      <Option value="banking">银行</Option>
                      <Option value="insurance">保险</Option>
                      <Option value="securities">证券</Option>
                      <Option value="fintech">金融科技</Option>
                    </Select>
                  </Form.Item>

                  <Form.Item
                    label="需求描述"
                    name="requirements"
                    rules={[{ required: true, message: '请输入需求描述' }]}
                  >
                    <TextArea rows={4} placeholder="请详细描述您的需求..." />
                  </Form.Item>

                  <Form.Item label="选择AI模型">
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                      {models.map(model => (
                        <Card
                          key={model.id}
                          size="small"
                          style={{
                            width: 200,
                            cursor: 'pointer',
                            border: selectedModels.includes(model.id) ? '2px solid #1890ff' : '1px solid #d9d9d9',
                            backgroundColor: selectedModels.includes(model.id) ? '#e6f7ff' : '#fff'
                          }}
                          onClick={() => {
                            if (selectedModels.includes(model.id)) {
                              setSelectedModels(selectedModels.filter(id => id !== model.id));
                            } else {
                              setSelectedModels([...selectedModels, model.id]);
                            }
                          }}
                        >
                          <div style={{ fontWeight: 'bold' }}>{model.name}</div>
                          <div style={{ fontSize: 12, color: '#666' }}>{model.provider}</div>
                          <div style={{ fontSize: 12, color: '#52c41a' }}>
                            成功率: {model.success_rate}%
                          </div>
                        </Card>
                      ))}
                    </div>
                  </Form.Item>

                  <Form.Item>
                    <Space>
                      <Button
                        type="primary"
                        icon={<RobotOutlined />}
                        loading={generating}
                        onClick={handleGenerate}
                        disabled={selectedModels.length === 0}
                      >
                        {generating ? '生成中...' : '开始生成'}
                      </Button>
                      <Button onClick={() => {
                        form.resetFields();
                        setSelectedModels([]);
                        setResults([]);
                      }}>
                        重置
                      </Button>
                    </Space>
                  </Form.Item>
                </Form>
              </Card>

              {/* 生成结果 */}
              {results.length > 0 && (
                <Card title="生成结果" style={{ marginTop: 16 }}>
                  <Table
                    columns={resultColumns}
                    dataSource={results}
                    rowKey="id"
                    pagination={false}
                  />
                </Card>
              )}

              {/* 可用模型展示 */}
              <Card title="可用AI模型" style={{ marginTop: 16 }} loading={loadingModels}>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 16 }}>
                  {models.map(model => (
                    <Card
                      key={model.id}
                      size="small"
                      style={{ width: 200, textAlign: 'center' }}
                    >
                      <div style={{ fontWeight: 'bold', marginBottom: 8 }}>{model.name}</div>
                      <div style={{ fontSize: 12, color: '#666', marginBottom: 4 }}>{model.provider}</div>
                      <div style={{ fontSize: 12, color: '#52c41a' }}>
                        成功率: {model.success_rate}%
                      </div>
                      <div style={{ fontSize: 12, color: '#999', marginTop: 8 }}>
                        {model.description}
                      </div>
                    </Card>
                  ))}
                </div>
                {models.length === 0 && !loadingModels && (
                  <p style={{ textAlign: 'center', color: '#999', marginTop: 32 }}>
                    暂无可用模型
                  </p>
                )}
              </Card>
            </div>
          )}

          {activeTab === 'proposals' && (
            <div>
              <Breadcrumb style={{ marginBottom: 16 }}>
                <Breadcrumb.Item>仪表盘</Breadcrumb.Item>
                <Breadcrumb.Item>方案管理</Breadcrumb.Item>
              </Breadcrumb>

              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
                <h2>方案管理</h2>
                <Button type="primary" icon={<PlusOutlined />} onClick={handleCreateProposal}>
                  创建新方案
                </Button>
              </div>

              <Card>
                <Table
                  columns={proposalColumns}
                  dataSource={proposals}
                  rowKey="id"
                  loading={loadingProposals}
                  pagination={{
                    pageSize: 10,
                    showSizeChanger: true,
                    showQuickJumper: true,
                    showTotal: (total) => `共 ${total} 条记录`,
                  }}
                />
              </Card>

              {proposals.length === 0 && !loadingProposals && (
                <Card style={{ textAlign: 'center', marginTop: 32 }}>
                  <p style={{ fontSize: 16, color: '#999' }}>暂无方案记录</p>
                  <p style={{ color: '#999' }}>创建您的第一个方案开始体验</p>
                  <Button
                    type="primary"
                    icon={<PlusOutlined />}
                    onClick={handleCreateProposal}
                  >
                    创建方案
                  </Button>
                </Card>
              )}

              {/* 创建方案模态框 */}
              <Modal
                title={editingProposal ? '编辑方案' : '创建新方案'}
                visible={showCreateProposalModal}
                onOk={handleSaveProposal}
                onCancel={() => {
    setShowCreateProposalModal(false);
    setEditingProposal(null);
    form.resetFields();
  }}
                confirmLoading={loading}
                width={800}
              >
                <Form form={form} layout="vertical">
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
                    <Form.Item
                      label="方案标题"
                      name="title"
                      rules={[{ required: true, message: '请输入方案标题' }]}
                    >
                      <Input placeholder="请输入方案标题" />
                    </Form.Item>
                    <Form.Item
                      label="客户名称"
                      name="clientName"
                      rules={[{ required: true, message: '请输入客户名称' }]}
                    >
                      <Input placeholder="请输入客户名称" />
                    </Form.Item>
                  </div>

                  <Form.Item
                    label="客户行业"
                    name="industry"
                    rules={[{ required: true, message: '请选择客户行业' }]}
                  >
                    <Select placeholder="请选择客户行业">
                      <Option value="banking">银行</Option>
                      <Option value="insurance">保险</Option>
                      <Option value="securities">证券</Option>
                      <Option value="fintech">金融科技</Option>
                    </Select>
                  </Form.Item>

                  <Form.Item
                    label="需求描述"
                    name="requirements"
                    rules={[{ required: true, message: '请输入需求描述' }]}
                  >
                    <TextArea rows={4} placeholder="请详细描述您的需求..." />
                  </Form.Item>

                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
                    <Form.Item
                      label="预算范围"
                      name="budgetRange"
                    >
                      <Input placeholder="例如：50-100万" />
                    </Form.Item>
                    <Form.Item
                      label="项目周期"
                      name="timeline"
                    >
                      <Input placeholder="例如：3个月" />
                    </Form.Item>
                  </div>
                </Form>
              </Modal>

              {/* 方案详情模态框 */}
              <Modal
                title="方案详情"
                visible={showProposalDetailModal}
                onCancel={() => setShowProposalDetailModal(false)}
                footer={[
                  <Button key="close" onClick={() => setShowProposalDetailModal(false)}>
                    关闭
                  </Button>,
                  viewingProposal?.status === 'draft' ? (
                    <Button
                      key="generate"
                      type="primary"
                      icon={<RobotOutlined />}
                      loading={generatingContent && editingProposal?.id === viewingProposal?.id}
                      onClick={() => {
                        handleGenerateContentInDetail(viewingProposal);
                      }}
                    >
                      生成内容
                    </Button>
                  ) : null,
                  viewingProposal?.status === 'completed' ? (
                    <Dropdown
                      overlay={
                        <AntdMenu>
                          <AntdMenu.Item
                            key="word"
                            icon={<DownloadOutlined />}
                            onClick={() => handleExport(viewingProposal, 'word')}
                          >
                            导出Word
                          </AntdMenu.Item>
                          <AntdMenu.Item
                            key="pdf"
                            icon={<DownloadOutlined />}
                            onClick={() => handleExport(viewingProposal, 'pdf')}
                          >
                            导出PDF
                          </AntdMenu.Item>
                          <AntdMenu.Item
                            key="excel"
                            icon={<DownloadOutlined />}
                            onClick={() => handleExport(viewingProposal, 'excel')}
                          >
                            导出报价单
                          </AntdMenu.Item>
                        </AntdMenu>
                      }
                    >
                      <Button key="export" icon={<DownloadOutlined />}>
                        导出
                      </Button>
                    </Dropdown>
                  ) : null,
                ]}
                width={1000}
              >
                {viewingProposal && (
                  <div style={{ maxHeight: 600, overflow: 'auto' }}>
                    <Row gutter={[16, 16]}>
                      <Col span={12}>
                        <p><strong>方案标题:</strong> {viewingProposal.title}</p>
                      </Col>
                      <Col span={12}>
                        <p><strong>客户名称:</strong> {viewingProposal.customer_name}</p>
                      </Col>
                      <Col span={12}>
                        <p><strong>所属行业:</strong> {viewingProposal.customer_industry}</p>
                      </Col>
                      <Col span={12}>
                        <p><strong>当前状态:</strong>
                          <Tag color={
                            viewingProposal.status === 'completed' ? 'green' :
                            viewingProposal.status === 'generating' ? 'blue' : 'orange'
                          }>
                            {viewingProposal.status === 'completed' ? '已完成' :
                             viewingProposal.status === 'generating' ? '生成中' : '草稿'}
                          </Tag>
                        </p>
                      </Col>
                      <Col span={24}>
                        <p><strong>需求描述:</strong></p>
                        <div style={{
                          background: '#f5f5f5',
                          padding: 12,
                          borderRadius: 4,
                          whiteSpace: 'pre-wrap'
                        }}>
                          {viewingProposal.requirements}
                        </div>
                      </Col>
                      {viewingProposal.budget_range && (
                        <Col span={12}>
                          <p><strong>预算范围:</strong> {viewingProposal.budget_range}</p>
                        </Col>
                      )}
                      {viewingProposal.timeline && (
                        <Col span={12}>
                          <p><strong>项目周期:</strong> {viewingProposal.timeline}</p>
                        </Col>
                      )}

                      {/* 在详情页面显示生成内容选择器 */}
                      {viewingProposal?.status === 'draft' && (
                        <Col span={24}>
                          <div style={{ marginTop: 20 }}>
                            <Alert
                              message="选择AI模型生成方案内容"
                              type="info"
                              style={{ marginBottom: 16 }}
                            />
                            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                              {models.map(model => (
                                <Card
                                  key={model.id}
                                  size="small"
                                  style={{
                                    width: 200,
                                    cursor: 'pointer',
                                    border: generateContentForm.selectedModels.includes(model.id) ? '2px solid #1890ff' : '1px solid #d9d9d9',
                                    backgroundColor: generateContentForm.selectedModels.includes(model.id) ? '#e6f7ff' : '#fff'
                                  }}
                                  onClick={() => {
                                    if (generateContentForm.selectedModels.includes(model.id)) {
                                      setGenerateContentForm({
                                        ...generateContentForm,
                                        selectedModels: generateContentForm.selectedModels.filter(id => id !== model.id)
                                      });
                                    } else {
                                      setGenerateContentForm({
                                        ...generateContentForm,
                                        selectedModels: [...generateContentForm.selectedModels, model.id]
                                      });
                                    }
                                  }}
                                >
                                  <div style={{ fontWeight: 'bold' }}>{model.name}</div>
                                  <div style={{ fontSize: 12, color: '#666' }}>{model.provider}</div>
                                  <div style={{ fontSize: 12, color: '#52c41a' }}>
                                    成功率: {model.success_rate}%
                                  </div>
                                </Card>
                              ))}
                            </div>
                          </div>
                        </Col>
                      )}

                      {viewingProposal.executive_summary && (
                        <Col span={24}>
                          <p><strong>执行摘要:</strong></p>
                          <div style={{
                            background: '#f0f8ff',
                            padding: 12,
                            borderRadius: 4,
                            whiteSpace: 'pre-wrap'
                          }}>
                            {viewingProposal.executive_summary}
                          </div>
                        </Col>
                      )}
                      {viewingProposal.full_content && (
                        <Col span={24}>
                          <p><strong>完整方案内容:</strong></p>
                          <div style={{
                            background: '#f9f9f9',
                            padding: 12,
                            borderRadius: 4,
                            whiteSpace: 'pre-wrap',
                            maxHeight: 300,
                            overflow: 'auto'
                          }}>
                            {viewingProposal.full_content}
                          </div>
                        </Col>
                      )}
                    </Row>
                  </div>
                )}
              </Modal>

              {/* 生成内容模态框 */}
              <Modal
                title="生成方案内容"
                visible={showGenerateContentModal}
                onOk={handleStartGeneration}
                onCancel={() => setShowGenerateContentModal(false)}
                confirmLoading={generatingContent}
                width={800}
              >
                {editingProposal && (
                  <div>
                    <Alert
                      message={`即将为方案"${editingProposal.title}"生成内容`}
                      type="info"
                      style={{ marginBottom: 16 }}
                    />

                    <Form layout="vertical">
                      <Form.Item label="选择AI模型">
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                          {models.map(model => (
                            <Card
                              key={model.id}
                              size="small"
                              style={{
                                width: 200,
                                cursor: 'pointer',
                                border: generateContentForm.selectedModels.includes(model.id) ? '2px solid #1890ff' : '1px solid #d9d9d9',
                                backgroundColor: generateContentForm.selectedModels.includes(model.id) ? '#e6f7ff' : '#fff'
                              }}
                              onClick={() => {
                                if (generateContentForm.selectedModels.includes(model.id)) {
                                  setGenerateContentForm({
                                    ...generateContentForm,
                                    selectedModels: generateContentForm.selectedModels.filter(id => id !== model.id)
                                  });
                                } else {
                                  setGenerateContentForm({
                                    ...generateContentForm,
                                    selectedModels: [...generateContentForm.selectedModels, model.id]
                                  });
                                }
                              }}
                            >
                              <div style={{ fontWeight: 'bold' }}>{model.name}</div>
                              <div style={{ fontSize: 12, color: '#666' }}>{model.provider}</div>
                              <div style={{ fontSize: 12, color: '#52c41a' }}>
                                成功率: {model.success_rate}%
                              </div>
                            </Card>
                          ))}
                        </div>
                      </Form.Item>
                    </Form>
                  </div>
                )}
              </Modal>
            </div>
          )}

          {activeTab === 'templates' && <TemplateManagement />}
          {activeTab === 'documents' && <DocumentManagement />}
          {activeTab === 'ai-models' && <AIModelConfig />}
          {activeTab === 'settings' && <SystemSettings />}
        </Content>
      </Layout>
    </Layout>
  );
};

// 主应用组件
function App() {
  const [isInitialized, setIsInitialized] = useState(false);

  useEffect(() => {
    // 检查本地存储的token
    const token = localStorage.getItem('auth_token');
    const path = window.location.pathname;

    if (!token && path !== '/login') {
      window.location.href = '/login';
    }

    setIsInitialized(true);
  }, []);

  if (!isInitialized) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh',
        fontSize: 16
      }}>
        正在初始化...
      </div>
    );
  }

  return (
    <ConfigProvider locale={zhCN}>
      <Router>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/proposal/:id" element={<ProposalDetailSimple />} />
          <Route path="/*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </Router>
    </ConfigProvider>
  );
}

export default App;