import React, { useState, useEffect } from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { ConfigProvider, Button, Card, Form, Input, Layout, Menu, Avatar, Space, message, Table, Tag, Spin, Modal, Select, Divider, List, Statistic, Row, Col } from 'antd'
import zhCN from 'antd/locale/zh_CN'
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
  SyncOutlined
} from '@ant-design/icons'

const { Header, Sider, Content } = Layout;
const { Option } = Select;
const { TextArea } = Input;

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

// 完整的仪表盘组件
const Dashboard = () => {
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

  useEffect(() => {
    if (activeTab === 'multi-model') {
      loadModels();
    }
    if (activeTab === 'proposals') {
      loadProposals();
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
            onClick={() => {
              Modal.info({
                title: `方案详情: ${record.title}`,
                width: 800,
                content: (
                  <div style={{ maxHeight: 400, overflow: 'auto' }}>
                    <p><strong>客户名称:</strong> {record.customer_name}</p>
                    <p><strong>行业:</strong> {record.customer_industry || '-'}</p>
                    <p><strong>需求描述:</strong></p>
                    <p>{record.requirements}</p>
                    <p><strong>执行摘要:</strong></p>
                    <p>{record.executive_summary || '暂无内容'}</p>
                  </div>
                ),
              });
            }}
          >
            查看
          </Button>
          {record.status === 'completed' && (
            <Button
              size="small"
              icon={<DownloadOutlined />}
              onClick={() => {
                message.info('导出功能开发中...');
              }}
            >
              导出
            </Button>
          )}
        </Space>
      ),
    },
  ];

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
                        <Button type="link" icon={<EyeOutlined />}>查看</Button>
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

              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
                gap: 20,
                marginTop: 30
              }}>
                <Card title="📝 方案管理" extra={<Button type="primary" onClick={() => setActiveTab('proposals')}>查看</Button>}>
                  <p>管理售前方案，创建和编辑方案内容</p>
                  <p>支持多种格式导出和模板应用</p>
                </Card>

                <Card title="🤖 AI模型" extra={<Button>配置</Button>}>
                  <p>配置和管理AI模型</p>
                  <p>支持Kimi、智谱AI、DeepSeek等模型</p>
                </Card>

                <Card title="📊 多模型生成" extra={<Button type="primary" onClick={() => setActiveTab('multi-model')}>使用</Button>}>
                  <p>使用多个AI模型同时生成方案</p>
                  <p>对比不同模型的生成效果</p>
                </Card>

                <Card title="📚 文档管理" extra={<Button>管理</Button>}>
                  <p>上传和管理参考文档</p>
                  <p>支持语义搜索和智能推荐</p>
                </Card>
              </div>

              <div style={{ marginTop: 30, padding: 20, backgroundColor: '#f0f8ff', borderRadius: 8 }}>
                <h3>系统功能特性</h3>
                <ul style={{ lineHeight: 1.8 }}>
                  <li>✅ <strong>多AI模型支持</strong> - 集成Kimi、智谱AI、DeepSeek等多种大模型</li>
                  <li>✅ <strong>同步生成对比</strong> - 同时使用多个模型生成方案，直观对比效果</li>
                  <li>✅ <strong>迭代优化功能</strong> - 基于用户反馈持续改进方案质量</li>
                  <li>✅ <strong>版本管理</strong> - 完整的方案版本历史和管理</li>
                  <li>✅ <strong>模板系统</strong> - 预定义方案模板，提高生成效率</li>
                  <li>✅ <strong>文档知识库</strong> - 语义搜索，智能推荐相关内容</li>
                </ul>
              </div>
            </div>
          )}

          {activeTab === 'multi-model' && (
            <div>
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
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
                <h2>方案管理</h2>
                <Button type="primary" icon={<PlusOutlined />}>
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
                  <p style={{ color: '#999' }}>请先使用多模型生成功能创建方案</p>
                  <Button
                    type="primary"
                    icon={<RobotOutlined />}
                    onClick={() => setActiveTab('multi-model')}
                  >
                    开始生成方案
                  </Button>
                </Card>
              )}
            </div>
          )}

          {activeTab === 'settings' && (
            <div>
              <h2>系统设置</h2>
              <Card style={{ marginTop: 16 }}>
                <p>系统设置功能正在开发中...</p>
                <Divider />
                <h4>用户信息</h4>
                <p>用户名: {currentUser?.username}</p>
                <p>角色: {currentUser?.role}</p>
                <Divider />
                <h4>系统配置</h4>
                <p>主题设置</p>
                <p>语言设置</p>
                <p>通知设置</p>
              </Card>
            </div>
          )}
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
          <Route path="/*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </Router>
    </ConfigProvider>
  );
}

export default App