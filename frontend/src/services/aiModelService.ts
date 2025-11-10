import api from './api'

export interface AIModelConfig {
  id: number
  name: string
  provider: string
  model_name: string
  api_key?: string
  base_url?: string
  max_tokens: number
  context_length: number
  temperature: number
  top_p: number
  frequency_penalty: number
  presence_penalty: number
  timeout: number
  max_retries: number
  headers?: Record<string, any>
  extra_params?: Record<string, any>
  is_enabled: boolean
  is_default: boolean
  description?: string
  total_calls: number
  success_calls: number
  total_tokens: number
  success_rate: number
  created_at: string
  updated_at: string
}

export interface CreateAIModelConfig {
  name: string
  provider: string
  model_name: string
  api_key?: string
  base_url?: string
  max_tokens?: number
  context_length?: number
  temperature?: number
  top_p?: number
  frequency_penalty?: number
  presence_penalty?: number
  timeout?: number
  max_retries?: number
  headers?: Record<string, any>
  extra_params?: Record<string, any>
  description?: string
  is_enabled?: boolean
}

export interface UpdateAIModelConfig {
  name?: string
  api_key?: string
  base_url?: string
  max_tokens?: number
  context_length?: number
  temperature?: number
  top_p?: number
  frequency_penalty?: number
  presence_penalty?: number
  timeout?: number
  max_retries?: number
  headers?: Record<string, any>
  extra_params?: Record<string, any>
  description?: string
  is_enabled?: boolean
}

export interface ModelTestRequest {
  prompt?: string
  temperature?: number
  max_tokens?: number
}

export interface ModelTestResponse {
  success: boolean
  response?: string
  error?: string
  duration_ms: number
  tokens_used?: number
}

export interface ModelProvider {
  name: string
  display_name: string
  description: string
}

export interface PresetModelConfig {
  name: string
  provider: string
  model_name: string
  base_url?: string
  max_tokens?: number
  context_length?: number
  temperature?: number
  top_p?: number
  frequency_penalty?: number
  presence_penalty?: number
  timeout?: number
  max_retries?: number
  description?: string
}

class AIModelService {
  // 获取所有模型配置
  async getModels(params?: {
    skip?: number
    limit?: number
    provider?: string
    is_enabled?: boolean
  }): Promise<{ data: AIModelConfig[]; total: number }> {
    const response = await api.get('/ai/models', { params })
    return response.data
  }

  // 获取启用的模型列表
  async getEnabledModels(): Promise<AIModelConfig[]> {
    const response = await api.get('/ai/models/enabled')
    return response.data
  }

  // 获取单个模型配置
  async getModel(id: number): Promise<AIModelConfig> {
    const response = await api.get(`/ai/models/${id}`)
    return response.data
  }

  // 创建模型配置
  async createModel(data: CreateAIModelConfig): Promise<AIModelConfig> {
    const response = await api.post('/ai/models', data)
    return response.data
  }

  // 更新模型配置
  async updateModel(id: number, data: UpdateAIModelConfig): Promise<AIModelConfig> {
    const response = await api.put(`/ai/models/${id}`, data)
    return response.data
  }

  // 删除模型配置
  async deleteModel(id: number): Promise<void> {
    await api.delete(`/ai/models/${id}`)
  }

  // 测试模型连接
  async testModel(id: number, data?: ModelTestRequest): Promise<ModelTestResponse> {
    const response = await api.post(`/ai/models/${id}/test`, {
      prompt: data?.prompt || '请简单介绍一下你自己。',
      temperature: data?.temperature,
      max_tokens: data?.max_tokens
    })
    return response.data
  }

  // 设置默认模型
  async setDefaultModel(id: number): Promise<void> {
    await api.post(`/ai/models/${id}/set-default`)
  }

  // 获取预设模型配置
  async getPresetModels(): Promise<PresetModelConfig[]> {
    const response = await api.get('/ai/models/presets')
    return response.data
  }

  // 导入预设模型
  async importPresetModel(presetName: string): Promise<AIModelConfig> {
    const response = await api.post(`/ai/models/presets/${presetName}`)
    return response.data
  }

  // 获取支持的供应商列表
  async getSupportedProviders(): Promise<{ providers: ModelProvider[] }> {
    const response = await api.get('/ai/models/providers')
    return response.data
  }
}

export default new AIModelService()
