import { useState } from 'react'
import { Form, Input, Button, Card, message } from 'antd'
import { useNavigate } from 'react-router-dom'
import { proposalService } from '../services/proposalService'

const ProposalCreate = () => {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [form] = Form.useForm()

  const onFinish = async (values: any) => {
    setLoading(true)
    try {
      const proposal = await proposalService.create(values)
      message.success('方案创建成功')
      navigate(`/proposals/${proposal.id}`)
    } catch (error) {
      console.error('创建失败:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <h1 style={{ marginBottom: 24 }}>创建方案</h1>

      <Card>
        <Form
          form={form}
          layout="vertical"
          onFinish={onFinish}
        >
          <Form.Item
            name="title"
            label="方案标题"
            rules={[{ required: true, message: '请输入方案标题' }]}
          >
            <Input placeholder="请输入方案标题" />
          </Form.Item>

          <Form.Item
            name="customer_name"
            label="客户名称"
            rules={[{ required: true, message: '请输入客户名称' }]}
          >
            <Input placeholder="请输入客户名称" />
          </Form.Item>

          <Form.Item
            name="customer_industry"
            label="客户行业"
          >
            <Input placeholder="请输入客户所属行业" />
          </Form.Item>

          <Form.Item
            name="customer_contact"
            label="客户联系方式"
          >
            <Input placeholder="请输入客户联系方式" />
          </Form.Item>

          <Form.Item
            name="requirements"
            label="客户需求"
            rules={[{ required: true, message: '请输入客户需求' }]}
          >
            <Input.TextArea
              rows={10}
              placeholder="请详细描述客户需求..."
            />
          </Form.Item>

          <Form.Item>
            <Button type="primary" htmlType="submit" loading={loading}>
              创建方案
            </Button>
            <Button style={{ marginLeft: 8 }} onClick={() => navigate('/proposals')}>
              取消
            </Button>
          </Form.Item>
        </Form>
      </Card>
    </div>
  )
}

export default ProposalCreate
