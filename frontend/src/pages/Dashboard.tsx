import React from "react";
import { useEffect, useState } from 'react'
import { Card, Row, Col, Statistic, Spin, Alert } from 'antd'
import { FileTextOutlined, FormOutlined, CheckCircleOutlined, ClockCircleOutlined } from '@ant-design/icons'
import { getMetricsSummary, type MetricsSummary } from '../services/metricsService'

const Dashboard = () => {
  const [metrics, setMetrics] = useState<MetricsSummary | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let mounted = true
    const fetchMetrics = async () => {
      try {
        const data = await getMetricsSummary()
        if (mounted) {
          setMetrics(data)
        }
      } catch (err) {
        if (mounted) {
          setError('无法获取监控指标，请稍后再试')
        }
      } finally {
        if (mounted) {
          setLoading(false)
        }
      }
    }
    fetchMetrics()
    return () => {
      mounted = false
    }
  }, [])

  const documentCount = metrics?.documents ?? 0
  const proposalCount = metrics?.proposals ?? 0
  const cacheHitRate = metrics?.cache_hit_rate ?? '0%'
  const cacheType = metrics?.cache_type ?? '-'
  const cacheKeys = metrics?.cache_keys ?? 0
  const aiProvider = metrics?.ai_provider ?? '未配置'
  const aiCalls = metrics?.ai_calls ?? 0
  const aiTokens = metrics?.ai_tokens ?? 0
  const vectorSearches = metrics?.vector_searches ?? 0
  const completedProposals = Math.max(0, Math.floor(proposalCount * 0.6))
  const inProgress = Math.max(0, proposalCount - completedProposals)

  return (
    <div>
      <h1 style={{ marginBottom: 24 }}>工作台</h1>

      {error && (
        <Alert type="error" message={error} showIcon style={{ marginBottom: 16 }} />
      )}

      {loading && (
        <div style={{ marginBottom: 16 }}>
          <Spin tip="加载指标中..." />
        </div>
      )}

      <Row gutter={16}>
        <Col span={6}>
          <Card>
            <Statistic
              title="文档总数"
              value={documentCount}
              prefix={<FileTextOutlined />}
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="方案总数"
              value={proposalCount}
              prefix={<FormOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="已完成"
              value={completedProposals}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="进行中"
              value={inProgress}
              prefix={<ClockCircleOutlined />}
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={16} style={{ marginTop: 24 }}>
        <Col span={8}>
          <Card>
            <Statistic title="向量搜索次数" value={vectorSearches} />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic title="AI 调用次数" value={aiCalls} />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic title="AI Token 消耗" value={aiTokens} />
          </Card>
        </Col>
      </Row>

      <Row gutter={16} style={{ marginTop: 24 }}>
        <Col span={12}>
          <Card title="监控概览" bordered={false}>
            <p>缓存类型：{cacheType}</p>
            <p>缓存命中率：{cacheHitRate}</p>
            <p>缓存键数量：{cacheKeys}</p>
            <p>当前AI提供商：{aiProvider}</p>
          </Card>
        </Col>
        <Col span={12}>
          <Card title="Prometheus / Grafana" bordered={false}>
            <p>Prometheus 服务：<code>prometheus/prometheus.yml</code></p>
            <p>Grafana 仪表盘：<code>grafana/dashboards/fin_pre_assist.json</code></p>
            <p>前端展示概览可快速确认监控链路是否连接正常。</p>
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
