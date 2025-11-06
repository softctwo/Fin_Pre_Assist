import { useState, useEffect } from 'react'
import { Button, Table, Upload, Modal, Form, Input, Select, message, Space, Tag } from 'antd'
import { UploadOutlined, DeleteOutlined } from '@ant-design/icons'
import { documentService, type Document } from '../services/documentService'
import type { UploadFile } from 'antd/es/upload/interface'

const Documents = () => {
  const [documents, setDocuments] = useState<Document[]>([])
  const [loading, setLoading] = useState(false)
  const [modalVisible, setModalVisible] = useState(false)
  const [fileList, setFileList] = useState<UploadFile[]>([])
  const [form] = Form.useForm()

  useEffect(() => {
    loadDocuments()
  }, [])

  const loadDocuments = async () => {
    setLoading(true)
    try {
      const data = await documentService.list()
      setDocuments(data.items)
    } catch (error) {
      console.error('加载文档失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleUpload = async (values: any) => {
    if (fileList.length === 0) {
      message.error('请选择文件')
      return
    }

    setLoading(true)
    try {
      const file = fileList[0].originFileObj as File
      await documentService.upload(file, values)
      message.success('上传成功')
      setModalVisible(false)
      form.resetFields()
      setFileList([])
      loadDocuments()
    } catch (error) {
      console.error('上传失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (id: number) => {
    Modal.confirm({
      title: '确认删除',
      content: '确定要删除这个文档吗？',
      onOk: async () => {
        try {
          await documentService.delete(id)
          message.success('删除成功')
          loadDocuments()
        } catch (error) {
          console.error('删除失败:', error)
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
      title: '类型',
      dataIndex: 'type',
      key: 'type',
      render: (type: string) => {
        const typeMap: Record<string, { text: string, color: string }> = {
          technical_proposal: { text: '技术方案', color: 'blue' },
          business_proposal: { text: '商务方案', color: 'green' },
          quotation: { text: '报价单', color: 'orange' },
          bid_document: { text: '投标文档', color: 'purple' },
          case_study: { text: '案例', color: 'cyan' },
        }
        const info = typeMap[type] || { text: type, color: 'default' }
        return <Tag color={info.color}>{info.text}</Tag>
      },
    },
    {
      title: '文件名',
      dataIndex: 'file_name',
      key: 'file_name',
    },
    {
      title: '行业',
      dataIndex: 'industry',
      key: 'industry',
    },
    {
      title: '客户',
      dataIndex: 'customer_name',
      key: 'customer_name',
    },
    {
      title: '上传时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date: string) => new Date(date).toLocaleString(),
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: Document) => (
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
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <h1>文档管理</h1>
        <Button
          type="primary"
          icon={<UploadOutlined />}
          onClick={() => setModalVisible(true)}
        >
          上传文档
        </Button>
      </div>

      <Table
        columns={columns}
        dataSource={documents}
        loading={loading}
        rowKey="id"
      />

      <Modal
        title="上传文档"
        open={modalVisible}
        onCancel={() => {
          setModalVisible(false)
          form.resetFields()
          setFileList([])
        }}
        footer={null}
      >
        <Form form={form} onFinish={handleUpload} layout="vertical">
          <Form.Item
            name="title"
            label="标题"
            rules={[{ required: true, message: '请输入标题' }]}
          >
            <Input placeholder="请输入文档标题" />
          </Form.Item>

          <Form.Item
            name="doc_type"
            label="文档类型"
            rules={[{ required: true, message: '请选择文档类型' }]}
          >
            <Select placeholder="请选择文档类型">
              <Select.Option value="technical_proposal">技术方案</Select.Option>
              <Select.Option value="business_proposal">商务方案</Select.Option>
              <Select.Option value="quotation">报价单</Select.Option>
              <Select.Option value="bid_document">投标文档</Select.Option>
              <Select.Option value="case_study">案例</Select.Option>
              <Select.Option value="other">其他</Select.Option>
            </Select>
          </Form.Item>

          <Form.Item name="industry" label="行业">
            <Input placeholder="请输入行业" />
          </Form.Item>

          <Form.Item name="customer_name" label="客户名称">
            <Input placeholder="请输入客户名称" />
          </Form.Item>

          <Form.Item label="文件">
            <Upload
              fileList={fileList}
              beforeUpload={(file) => {
                setFileList([file as any])
                return false
              }}
              onRemove={() => setFileList([])}
              maxCount={1}
            >
              <Button icon={<UploadOutlined />}>选择文件</Button>
            </Upload>
          </Form.Item>

          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit" loading={loading}>
                上传
              </Button>
              <Button onClick={() => {
                setModalVisible(false)
                form.resetFields()
                setFileList([])
              }}>
                取消
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

export default Documents
