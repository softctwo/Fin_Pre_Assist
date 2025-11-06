import { useState, useEffect } from 'react'
import { Button, Table, Modal, Form, Input, Select, message, Space, Tag, Card } from 'antd'
import { PlusOutlined, DeleteOutlined, SearchOutlined } from '@ant-design/icons'
import api from '../services/api'
import { searchService } from '../services/searchService'

const { TextArea } = Input

const Knowledge = () => {
  const [knowledge, setKnowledge] = useState<any[]>([])
  const [categories, setCategories] = useState<string[]>([])
  const [loading, setLoading] = useState(false)
  const [modalVisible, setModalVisible] = useState(false)
  const [searchResults, setSearchResults] = useState<any[]>([])
  const [form] = Form.useForm()
  const [searchForm] = Form.useForm()

  useEffect(() => {
    loadKnowledge()
    loadCategories()
  }, [])

  const loadKnowledge = async () => {
    setLoading(true)
    try {
      const response = await api.get('/knowledge/')
      setKnowledge(response.data.items)
    } catch (error) {
      console.error('加载知识库失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadCategories = async () => {
    try {
      const response = await api.get('/knowledge/categories')
      setCategories(response.data.categories)
    } catch (error) {
      console.error('加载分类失败:', error)
    }
  }

  const handleCreate = async (values: any) => {
    setLoading(true)
    try {
      await api.post('/knowledge/', values)
      message.success('创建成功')
      setModalVisible(false)
      form.resetFields()
      loadKnowledge()
      loadCategories()
    } catch (error) {
      message.error('创建失败')
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = async (values: any) => {
    if (!values.query) {
      message.warning('请输入搜索关键词')
      return
    }

    setLoading(true)
    try {
      const result = await searchService.searchKnowledge({
        query: values.query,
        limit: 10,
        category: values.category
      })
      setSearchResults(result.results)
      message.success(`找到 ${result.total} 条相关知识`)
    } catch (error) {
      message.error('搜索失败')
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (id: number) => {
    Modal.confirm({
      title: '确认删除',
      content: '确定要删除这条知识吗？',
      onOk: async () => {
        try {
          await api.delete(`/knowledge/${id}`)
          message.success('删除成功')
          loadKnowledge()
        } catch (error) {
          message.error('删除失败')
        }
      },
    })
  }

  const columns = [
    {
      title: '标题',
      dataIndex: 'title',
      key: 'title',
    },
    {
      title: '分类',
      dataIndex: 'category',
      key: 'category',
      render: (category: string) => <Tag color="blue">{category}</Tag>,
    },
    {
      title: '标签',
      dataIndex: 'tags',
      key: 'tags',
      render: (tags: string[]) =>
        tags?.map((tag, index) => (
          <Tag key={index} color="green">
            {tag}
          </Tag>
        )),
    },
    {
      title: '权重',
      dataIndex: 'weight',
      key: 'weight',
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
      render: (_: any, record: any) => (
        <Space>
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
      <h1>知识库</h1>

      <Card title="智能搜索" style={{ marginBottom: 24 }}>
        <Form form={searchForm} onFinish={handleSearch} layout="inline">
          <Form.Item name="query" style={{ width: 400 }}>
            <Input placeholder="输入关键词进行语义搜索..." />
          </Form.Item>
          <Form.Item name="category">
            <Select placeholder="选择分类" style={{ width: 150 }} allowClear>
              {categories.map((cat) => (
                <Select.Option key={cat} value={cat}>
                  {cat}
                </Select.Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" icon={<SearchOutlined />} loading={loading}>
              搜索
            </Button>
          </Form.Item>
        </Form>

        {searchResults.length > 0 && (
          <div style={{ marginTop: 16 }}>
            <h3>搜索结果：</h3>
            {searchResults.map((result, index) => (
              <Card key={index} size="small" style={{ marginBottom: 8 }}>
                <div>
                  <strong>{result.metadata.title}</strong>
                  <Tag color="blue" style={{ marginLeft: 8 }}>
                    {result.metadata.category}
                  </Tag>
                  <Tag color="green">相关度: {(result.relevance_score * 100).toFixed(0)}%</Tag>
                </div>
                <p style={{ marginTop: 8, color: '#666' }}>{result.content}</p>
              </Card>
            ))}
          </div>
        )}
      </Card>

      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <h2>所有知识</h2>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setModalVisible(true)}>
          添加知识
        </Button>
      </div>

      <Table columns={columns} dataSource={knowledge} loading={loading} rowKey="id" />

      <Modal
        title="添加知识"
        open={modalVisible}
        onCancel={() => {
          setModalVisible(false)
          form.resetFields()
        }}
        footer={null}
        width={800}
      >
        <Form form={form} onFinish={handleCreate} layout="vertical">
          <Form.Item
            name="category"
            label="分类"
            rules={[{ required: true, message: '请输入分类' }]}
          >
            <Input placeholder="如：产品介绍、解决方案、技术文档等" />
          </Form.Item>

          <Form.Item
            name="title"
            label="标题"
            rules={[{ required: true, message: '请输入标题' }]}
          >
            <Input placeholder="请输入知识标题" />
          </Form.Item>

          <Form.Item
            name="content"
            label="内容"
            rules={[{ required: true, message: '请输入内容' }]}
          >
            <TextArea rows={10} placeholder="请输入详细内容" />
          </Form.Item>

          <Form.Item name="tags" label="标签">
            <Select mode="tags" placeholder="输入标签后按回车" />
          </Form.Item>

          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit" loading={loading}>
                添加
              </Button>
              <Button
                onClick={() => {
                  setModalVisible(false)
                  form.resetFields()
                }}
              >
                取消
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

export default Knowledge
