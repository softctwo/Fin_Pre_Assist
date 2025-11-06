import { Card, Row, Col, Statistic } from 'antd'
import { FileTextOutlined, FormOutlined, CheckCircleOutlined, ClockCircleOutlined } from '@ant-design/icons'

const Dashboard = () => {
  return (
    <div>
      <h1 style={{ marginBottom: 24 }}>工作台</h1>

      <Row gutter={16}>
        <Col span={6}>
          <Card>
            <Statistic
              title="文档总数"
              value={0}
              prefix={<FileTextOutlined />}
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="方案总数"
              value={0}
              prefix={<FormOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="已完成"
              value={0}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="进行中"
              value={0}
              prefix={<ClockCircleOutlined />}
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={16} style={{ marginTop: 24 }}>
        <Col span={12}>
          <Card title="最近文档" bordered={false}>
            <p>暂无数据</p>
          </Card>
        </Col>
        <Col span={12}>
          <Card title="最近方案" bordered={false}>
            <p>暂无数据</p>
          </Card>
        </Col>
      </Row>
    </div>
  )
}

export default Dashboard
