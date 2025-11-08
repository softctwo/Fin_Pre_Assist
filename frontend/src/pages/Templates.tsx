import React from "react";
import { useState, useEffect } from 'react'
import { Button, Table, Modal, Form, Input, Select, message, Space, Tag } from 'antd'
import { PlusOutlined, EyeOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons'
import { templateService } from '../services/templateService'

const { TextArea } = Input

const Templates = () => {
  const [templates, setTemplates] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [modalVisible, setModalVisible] = useState(false)
  const [previewVisible, setPreviewVisible] = useState(false)
  const [previewContent, setPreviewContent] = useState('')
  const [form] = Form.useForm()

  useEffect(() => {
    loadTemplates()
  }, [])

  const loadTemplates = async () => {
    setLoading(true)
    try {
      const data = await templateService.list()
      setTemplates(data.items)
    } catch (error) {
      console.error('加载模板失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCreate = async (values: any) => {
    setLoading(true)
    try {
      await templateService.create(values)
      message.success('创建成功')
      setModalVisible(false)
      form.resetFields()
      loadTemplates()
    } catch (error) {
      console.error('创建失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const handlePreview = async (template: any) => {
    try {
      const { variables } = await templateService.getVariables(template.id)

      // 使用默认值进行预览
      const sampleData: Record<string, string> = {}
      variables.forEach((v: string) => {
        sampleData[v] = `[${v}示例]`
      })

      const result = await templateService.preview(template.id, sampleData)
      setPreviewContent(result.preview)
      setPreviewVisible(true)
    } catch (error) {
      message.error('预览失败')
    }
  }

  const handleDelete = async (id: number) => {
    Modal.confirm({
      title: '确认删除',
      content: '确定要删除这个模板吗？',
      onOk: async () => {
        try {
          await templateService.delete(id)
          message.success('删除成功')
          loadTemplates()
        } catch (error) {
          message.error('删除失败')
        }
      },
    })
  }

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
      render: (type: string) => {
        const typeMap: Record<string, { text: string, color: string }> = {
          proposal: { text: '方案模板', color: 'blue' },
          quotation: { text: '报价单', color: 'green' },
          contract: { text: '合同', color: 'orange' },
          presentation: { text: '演示文稿', color: 'purple' },
        }
        const info = typeMap[type] || { text: type, color: 'default' }
        return <Tag color={info.color}>{info.text}</Tag>
      },
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
    },
    {
      title: '默认',
      dataIndex: 'is_default',
      key: 'is_default',
      render: (isDefault: number) => isDefault === 1 ? <Tag color="gold">默认</Tag> : null,
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
            icon={<EyeOutlined />}
            onClick={() => handlePreview(record)}
          >
            预览
          </Button>
          <Button
            type="link"
            icon={<EditOutlined />}
          >
            编辑
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
        <h1>模板管理</h1>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={() => setModalVisible(true)}
        >
          创建模板
        </Button>
      </div>

      <Table
        columns={columns}
        dataSource={templates}
        loading={loading}
        rowKey="id"
      />

      <Modal
        title="创建模板"
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
            name="name"
            label="模板名称"
            rules={[{ required: true, message: '请输入模板名称' }]}
          >
            <Input placeholder="请输入模板名称" />
          </Form.Item>

          <Form.Item
            name="type"
            label="模板类型"
            rules={[{ required: true, message: '请选择模板类型' }]}
          >
            <Select placeholder="请选择模板类型">
              <Select.Option value="proposal">方案模板</Select.Option>
              <Select.Option value="quotation">报价单</Select.Option>
              <Select.Option value="contract">合同</Select.Option>
              <Select.Option value="presentation">演示文稿</Select.Option>
            </Select>
          </Form.Item>

          <Form.Item name="description" label="描述">
            <Input placeholder="请输入描述" />
          </Form.Item>

          <Form.Item
            name="content"
            label="模板内容"
            rules={[{ required: true, message: '请输入模板内容' }]}
            extra="支持使用 {{ variable_name }} 格式定义变量"
          >
            <TextArea
              rows={15}
              placeholder="请输入模板内容，使用 {{ variable_name }} 定义变量"
              style={{ fontFamily: 'monospace' }}
            />
          </Form.Item>

          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit" loading={loading}>
                创建
              </Button>
              <Button onClick={() => {
                setModalVisible(false)
                form.resetFields()
              }}>
                取消
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      <Modal
        title="模板预览"
        open={previewVisible}
        onCancel={() => setPreviewVisible(false)}
        footer={[
          <Button key="close" onClick={() => setPreviewVisible(false)}>
            关闭
          </Button>
        ]}
        width={800}
      >
        <div style={{ whiteSpace: 'pre-wrap', maxHeight: '600px', overflow: 'auto' }}>
          {previewContent}
        </div>
      </Modal>
    </div>
  )
}

export default Templates
