import React, { useState, useEffect } from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { ConfigProvider, Button, Card, Form, Input, Layout, Menu, Avatar, Dropdown, Space, message, Table, Tag, Spin, Modal, Tabs } from 'antd'
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
  EditOutlined
} from '@ant-design/icons'

const { Header, Sider, Content } = Layout;
const { TabPane } = Tabs;

// 导入服务
import { authService } from './services/authService'
import { useAuthStore } from './store/authStore'
import multiModelProposalService from './services/multiModelProposalService'

// 多模型方案生成组件
const MultiModelGenerator = () => {
  const [models, setModels] = useState([]);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [selectedModels, setSelectedModels] = useState([]);
  const [results, setResults] = useState([]);
  const [proposalData, setProposalData] = useState({
    title: '',
    customer_name: '',
    requirements: '',
    customer_industry: 'banking'
  });
  const [form] = Form.useForm();

  useEffect(() => {
    loadModels();
  }, []);

  const loadModels = async () => {
    try {
      setLoading(true);
      const data = await multiModelProposalService.getAvailableModels();
      setModels(data);
    } catch (error) {
      console.error('加载模型失败:', error);
      message.error('加载模型失败');
    } finally {
      setLoading(false);
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

      const promises = selectedModels.map(modelId =>
        multiModelProposalService.generateProposal({
          ...values,
          model_id: modelId
        })
      );

      const results = await Promise.all(promises);
      setResults(results.map((result, index) => ({
        id: result.id,
        model: models.find(m => m.id === selectedModels[index])?.name || `Model ${index + 1}`,
        title: result.title,
        status: result.status,
        executive_summary: result.executive_summary,
        solution_overview: result.solution_overview,
        full_content: result.full_content,
        created_at: result.created_at
      })));

      message.success('方案生成完成！');
    } catch (error) {
      console.error('生成失败:', error);
      message.error('生成失败: ' + (error.message || '未知错误'));
    } finally {
      setGenerating(false);
    }
  };

  const columns = [
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
        <Tag color={status === 'completed' ? 'green' : 'processing'}>
          {status === 'completed' ? '已完成' : '生成中'}
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
            }}
          >
            查看
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <Card title="多模型方案生成" style={{ marginBottom: 16 }} loading={loading}>
        <Form form={form} layout="vertical" initialValues={proposalData}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
            <Form.Item
              label="方案标题"
              name="title"
              rules={[{ required: true, message: '请输入方案标题' }]}
            >
              <Input />
            </Form.Item>
            <Form.Item
              label="客户名称"
              name="customer_name"
              rules={[{ required: true, message: '请输入客户名称' }]}
            >
              <Input />
            </Form.Item>
          </div>

          <Form.Item
            label="客户行业"
            name="customer_industry"
          >
            <select style={{ width: '100%', padding: 8, border: '1px solid #d9d9d9', borderRadius: 4 }}>
              <option value="banking">银行</option>
              <option value="insurance">保险</option>
              <option value="securities">证券</option>
              <option value="fintech">金融科技</option>
            </select>
          </Form.Item>

          <Form.Item
            label="需求描述"
            name="requirements"
            rules={[{ required: true, message: '请输入需求描述' }]}
          >
            <Input.TextArea rows={4} />
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

      {results.length > 0 && (
        <Card title="生成结果">
          <Table
            columns={columns}
            dataSource={results}
            rowKey="id"
            pagination={false}
          />
        </Card>
      )}
    </div>
  );
};

// 主页面
const Dashboard = () => {
  const [user, logout] = useAuthStore((state) => state);
  const [activeTab, setActiveTab] = useState('overview');

  const handleLogout = () => {
    logout();
    message.success('已退出登录');
  };

  const userMenu = (
    <Menu>
      <Menu.Item key="profile" icon={<UserOutlined />}>
        个人资料
      </Menu.Item>
      <Menu.Divider />
      <Menu.Item key="logout" icon={<LogoutOutlined />} onClick={handleLogout}>
        退出登录
      </Menu.Item>
    </Menu>
  );

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
            <span>欢迎，{user?.username || '用户'}</span>
            <Dropdown overlay={userMenu} placement="bottomRight">
              <Avatar icon={<UserOutlined />} style={{ cursor: 'pointer' }} />
            </Dropdown>
          </Space>
        </Header>

        <Content style={{
          margin: '24px 16px',
          padding: 24,
          background: '#fff',
          borderRadius: 8,
          minHeight: 280
        }}>
          <Tabs activeKey={activeTab} onChange={setActiveTab}>
            <TabPane tab="系统概览" key="overview">
              <div>
                <h1>欢迎使用金融售前方案辅助系统</h1>

                <div style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
                  gap: 20,
                  marginTop: 30
                }}>
                  <Card title="📝 方案管理" extra={<Button type="primary">查看</Button>}>
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
            </TabPane>

            <TabPane tab="多模型生成" key="multi-model">
              <MultiModelGenerator />
            </TabPane>

            <TabPane tab="方案管理" key="proposals">
              <div>
                <h2>方案管理</h2>
                <Card style={{ marginTop: 16 }}>
                  <p>方案管理功能正在开发中...</p>
                  <Button type="primary" icon={<PlusOutlined />}>
                    创建新方案
                  </Button>
                </Card>
              </div>
            </TabPane>

            <TabPane tab="系统设置" key="settings">
              <div>
                <h2>系统设置</h2>
                <Card style={{ marginTop: 16 }}>
                  <p>系统设置功能正在开发中...</p>
                </Card>
              </div>
            </TabPane>
          </Tabs>
        </Content>
      </Layout>
    </Layout>
  );
};

// 登录组件
const Login = () => {
  const [loading, setLoading] = useState(false);
  const { setAuth } = useAuthStore();

  const onFinish = async (values: any) => {
    setLoading(true);
    try {
      const data = await authService.login(values);
      console.log('登录成功:', data);

      // 获取用户信息
      try {
        const user = await authService.getCurrentUser();
        setAuth(data.access_token, user);
        message.success('登录成功！');
      } catch (userError) {
        // 如果获取用户信息失败，先保存token
        setAuth(data.access_token, {
          id: 1,
          username: values.username,
          email: '',
          full_name: '',
          role: 'admin'
        });
        message.success('登录成功！');
      }
    } catch (error: any) {
      console.error('登录失败:', error);
      message.error(error.response?.data?.detail || '登录失败');
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
      <Card
        title={
          <div style={{ textAlign: 'center' }}>
            <h2 style={{ color: '#1890ff', margin: 0 }}>金融售前方案辅助系统</h2>
            <p style={{ color: '#666', margin: '10px 0 0 0' }}>Multi-Model Proposal Generation System</p>
          </div>
        }
        style={{
          width: 420,
          boxShadow: '0 8px 32px rgba(0,0,0,0.1)',
          borderRadius: 12
        }}
      >
        <Form onFinish={onFinish} layout="vertical" size="large">
          <Form.Item
            label="用户名"
            name="username"
            rules={[{ required: true, message: '请输入用户名' }]}
          >
            <Input
              prefix={<UserOutlined />}
              placeholder="请输入用户名"
            />
          </Form.Item>

          <Form.Item
            label="密码"
            name="password"
            rules={[{ required: true, message: '请输入密码' }]}
          >
            <Input.Password
              prefix={<UserOutlined />}
              placeholder="请输入密码"
            />
          </Form.Item>

          <Form.Item>
            <Button
              type="primary"
              htmlType="submit"
              loading={loading}
              block
              style={{ height: 40, fontSize: 16 }}
            >
              {loading ? '登录中...' : '登录'}
            </Button>
          </Form.Item>
        </Form>

        <div style={{
          marginTop: 24,
          padding: 16,
          backgroundColor: '#f8f9fa',
          borderRadius: 8,
          fontSize: 12,
          color: '#666'
        }}>
          <p style={{ margin: 0, fontWeight: 'bold', marginBottom: 8 }}>测试账户：</p>
          <p style={{ margin: '4px 0' }}>用户名: <code>admin</code></p>
          <p style={{ margin: '4px 0' }}>密码: <code>admin123</code></p>
        </div>
      </Card>
    </div>
  );
};

// 受保护路由组件
const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const token = useAuthStore((state) => state.token);
  return token ? <>{children}</> : <Navigate to="/login" replace />;
};

// 主应用组件
function App() {
  const [isInitialized, setIsInitialized] = useState(false);
  const token = useAuthStore((state) => state.token);

  useEffect(() => {
    // 检查本地存储的token
    const storedAuth = localStorage.getItem('auth-storage');
    if (storedAuth) {
      try {
        const auth = JSON.parse(storedAuth);
        if (auth.state?.token) {
          console.log('发现本地token，用户已登录');
        }
      } catch (error) {
        console.error('解析本地token失败:', error);
      }
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
          <Route
            path="/*"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />
        </Routes>
      </Router>
    </ConfigProvider>
  );
}

export default App