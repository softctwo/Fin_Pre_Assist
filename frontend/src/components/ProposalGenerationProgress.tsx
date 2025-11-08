import { Modal, Progress, Alert, Typography } from 'antd'
import { useEffect, useState, useRef } from 'react'
import { useAuthStore } from '../store/authStore'

const { Text } = Typography

interface ProposalGenerationProgressProps {
  visible: boolean
  proposalId: number
  onComplete: (success: boolean, data?: any) => void
  onCancel: () => void
}

const ProposalGenerationProgress: React.FC<ProposalGenerationProgressProps> = ({
  visible,
  proposalId,
  onComplete,
  onCancel
}) => {
  const [progress, setProgress] = useState(0)
  const [stage, setStage] = useState('connecting')
  const [message, setMessage] = useState('正在连接...')
  const [error, setError] = useState<string | null>(null)
  const wsRef = useRef<WebSocket | null>(null)
  const { user } = useAuthStore()
  
  // 阶段文本映射
  const stageText: Record<string, string> = {
    connecting: '正在连接',
    initializing: '初始化',
    searching: '搜索中',
    preparing: '准备中',
    generating: '生成中',
    processing: '处理中',
    finalizing: '整理中',
    completed: '完成',
    error: '错误'
  }
  
  // 阶段颜色映射
  const getProgressStatus = () => {
    if (error) return 'exception'
    if (stage === 'completed') return 'success'
    return 'active'
  }
  
  useEffect(() => {
    if (!visible || !proposalId || !user?.id) return
    
    // 建立WebSocket连接 - 使用现有端点格式 /ws/{user_id}
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = window.location.hostname
    const port = import.meta.env.DEV ? '8000' : window.location.port
    const wsUrl = `${protocol}//${host}:${port}/api/v1/ws/${user.id}`
    
    console.log('建立WebSocket连接:', wsUrl)
    
    const ws = new WebSocket(wsUrl)
    wsRef.current = ws
    
    ws.onopen = () => {
      console.log('WebSocket连接已建立')
      setStage('connected')
      setMessage('连接成功,等待生成...')
    }
    
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        console.log('收到WebSocket消息:', data)
        
        // 处理方案生成进度消息(对应send_proposal_progress推送格式)
        if (data.type === 'proposal_progress' && data.proposal_id === proposalId) {
          setProgress(data.progress)
          setStage(data.stage)
          setMessage(data.message || stageText[data.stage] || data.stage)
          
          // 生成完成
          if (data.stage === 'completed' || data.progress === 100) {
            setProgress(100)
            setStage('completed')
            setMessage('方案生成完成!')
            setTimeout(() => {
              ws.close()
              onComplete(true, { id: proposalId })
            }, 1500)
          }
          
          // 生成失败
          if (data.stage === 'error') {
            setError(data.message || '生成失败')
            setStage('error')
            setTimeout(() => {
              ws.close()
            }, 2000)
          }
        }
        
        // 处理连接消息
        if (data.type === 'connection') {
          console.log('WebSocket连接确认:', data.message)
        }
      } catch (err) {
        console.error('解析WebSocket消息失败:', err)
      }
    }
    
    ws.onerror = (error) => {
      console.error('WebSocket错误:', error)
      setError('连接失败,请稍后重试')
      setStage('error')
    }
    
    ws.onclose = () => {
      console.log('WebSocket连接已关闭')
    }
    
    // 清理
    return () => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.close()
      }
    }
  }, [visible, proposalId, user?.id, onComplete])
  
  const handleCancel = () => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      // 发送取消消息(可选)
      try {
        wsRef.current.send(JSON.stringify({ action: 'cancel' }))
      } catch (err) {
        console.error('发送取消消息失败:', err)
      }
      wsRef.current.close()
    }
    onCancel()
  }
  
  return (
    <Modal
      title="方案生成中"
      open={visible}
      onCancel={handleCancel}
      footer={null}
      closable={stage === 'completed' || !!error}
      maskClosable={false}
      width={500}
    >
      <div style={{ padding: '20px 0' }}>
        {error ? (
          <Alert 
            message="生成失败" 
            description={error} 
            type="error" 
            showIcon 
          />
        ) : (
          <>
            <Progress
              percent={progress}
              status={getProgressStatus()}
              strokeColor={{
                '0%': '#1890ff',
                '100%': '#52c41a',
              }}
              style={{ marginBottom: 16 }}
            />
            <div style={{ textAlign: 'center' }}>
              <Text strong style={{ fontSize: 16, color: '#1890ff' }}>
                {stageText[stage] || stage}
              </Text>
              {message && (
                <div style={{ marginTop: 8, color: '#666' }}>
                  <Text type="secondary">{message}</Text>
                </div>
              )}
            </div>
            {stage === 'completed' && (
              <div style={{ marginTop: 16, textAlign: 'center' }}>
                <Text type="success">🎉 方案生成成功!</Text>
              </div>
            )}
          </>
        )}
      </div>
    </Modal>
  )
}

export default ProposalGenerationProgress
