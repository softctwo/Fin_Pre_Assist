import React, { useState, useEffect } from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { ConfigProvider, Button, Card, Form, Input, Layout, Menu, Avatar, Space, message } from 'antd'
import zhCN from 'antd/locale/zh_CN'
import {
  UserOutlined,
  LogoutOutlined,
  DashboardOutlined,
  FileTextOutlined,
  SettingOutlined,
  RobotOutlined
} from '@ant-design/icons'

const { Header, Sider, Content } = Layout;

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

// 简化的仪表盘组件
const Dashboard = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [models, setModels] = useState([]);
  const [loadingModels, setLoadingModels] = useState(false);

  useEffect(() => {
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

  const handleLogout = () => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user_info');
    message.success('已退出登录');
    window.location.href = '/login';
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
            <span>欢迎，admin</span>
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
          )}

          {activeTab === 'multi-model' && (
            <div>
              <h2>多模型方案生成</h2>
              <Card style={{ marginTop: 16 }} loading={loadingModels}>
                <h3>可用AI模型</h3>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 16, marginTop: 16 }}>
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

              <Card title="生成方案" style={{ marginTop: 16 }}>
                <p>方案生成功能正在完善中...</p>
                <Button type="primary">开始生成</Button>
              </Card>
            </div>
          )}

          {activeTab === 'proposals' && (
            <div>
              <h2>方案管理</h2>
              <Card style={{ marginTop: 16 }}>
                <p>方案管理功能正在开发中...</p>
                <Button type="primary">创建新方案</Button>
              </Card>
            </div>
          )}

          {activeTab === 'settings' && (
            <div>
              <h2>系统设置</h2>
              <Card style={{ marginTop: 16 }}>
                <p>系统设置功能正在开发中...</p>
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