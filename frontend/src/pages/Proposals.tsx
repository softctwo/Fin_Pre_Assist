import { useState, useEffect } from 'react'
import { Button, Table, Modal, Space, Tag, message } from 'antd'
import { PlusOutlined, EyeOutlined, DeleteOutlined } from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import { proposalService, type Proposal } from '../services/proposalService'

const Proposals = () => {
  const navigate = useNavigate()
  const [proposals, setProposals] = useState<Proposal[]>([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    loadProposals()
  }, [])

  const loadProposals = async () => {
    setLoading(true)
    try {
      const data = await proposalService.list()
      setProposals(data.items)
    } catch (error) {
      console.error('加载方案失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (id: number) => {
    Modal.confirm({
      title: '确认删除',
      content: '确定要删除这个方案吗？',
      onOk: async () => {
        try {
          await proposalService.delete(id)
          message.success('删除成功')
          loadProposals()
        } catch (error) {
          console.error('删除失败:', error)
        }
      },
    })
  }

  const columns = [
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
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => {
        const statusMap: Record<string, { text: string, color: string }> = {
          draft: { text: '草稿', color: 'default' },
          generating: { text: '生成中', color: 'processing' },
          completed: { text: '已完成', color: 'success' },
          exported: { text: '已导出', color: 'cyan' },
          archived: { text: '已归档', color: 'default' },
        }
        const info = statusMap[status] || { text: status, color: 'default' }
        return <Tag color={info.color}>{info.text}</Tag>
      },
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date: string) => new Date(date).toLocaleString(),
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: Proposal) => (
        <Space>
          <Button
            type="link"
            icon={<EyeOutlined />}
            onClick={() => navigate(`/proposals/${record.id}`)}
          >
            查看
          </Button>
          <Button
            type="link"
            danger
            icon={<DeleteOutlined />}
            onClick={() => handleDelete(record.id)}
          >
            删除
          </Button>
        </Space>
      ),
    },
  ]

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <h1>方案管理</h1>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={() => navigate('/proposals/create')}
        >
          创建方案
        </Button>
      </div>

      <Table
        columns={columns}
        dataSource={proposals}
        loading={loading}
        rowKey="id"
      />
    </div>
  )
}

export default Proposals
