import api from './api'
import { AIModelConfig } from './aiModelService'

export interface MultiModelProposalCreate {
  title: string
  customer_name: string
  customer_industry?: string
  customer_contact?: string
  requirements: string
  model_id: number
  reference_document_ids?: number[]
  reference_template_id?: number
}

export interface ModelSelectionResponse {
  id: number
  name: string
  provider: string
  model_name: string
  is_enabled: boolean
  description?: string
  success_rate: number
}

export interface MultiModelProposalResponse {
  id: number
  title: string
  customer_name: string
  requirements: string
  executive_summary?: string
  solution_overview?: string
  technical_details?: string
  implementation_plan?: string
  pricing?: Record<string, any>
  full_content?: string
  status: string
  created_at: string
  updated_at: string
}

export interface PreviewResponse {
  preview: {
    executive_summary?: string
    solution_overview?: string
    technical_details?: string
    implementation_plan?: string
    pricing?: Record<string, any>
    full_content?: string
  }
  model_info: {
    id: number
    name: string
    provider: string
    model_name: string
  }
}

export interface ModelStatsResponse {
  model: ModelSelectionResponse
  total_calls: number
  success_calls: number
  total_tokens: number
  success_rate: number
  created_at: string
  updated_at: string
}

export interface ComparisonResponse {
  proposal_data: MultiModelProposalCreate
  comparisons: Array<{
    model: ModelSelectionResponse
    result?: PreviewResponse['preview']
    success: boolean
    error?: string
  }>
  total_models: number
  successful_models: number
}

class MultiModelProposalService {
  // 获取可用模型列表
  async getAvailableModels(): Promise<ModelSelectionResponse[]> {
    const response = await api.get('/multi-model-proposals/models/available')
    return response.data
  }

  // 获取默认模型
  async getDefaultModel(): Promise<ModelSelectionResponse> {
    const response = await api.get('/multi-model-proposals/models/default')
    return response.data
  }

  // 使用指定模型生成方案
  async generateProposal(data: MultiModelProposalCreate): Promise<MultiModelProposalResponse> {
    const response = await api.post('/multi-model-proposals/generate', data)
    return response.data
  }

  // 预览方案生成效果
  async previewProposal(data: MultiModelProposalCreate): Promise<PreviewResponse> {
    const response = await api.post('/multi-model-proposals/preview', data)
    return response.data
  }

  // 获取模型使用统计
  async getModelStats(modelId: number): Promise<ModelStatsResponse> {
    const response = await api.get(`/multi-model-proposals/models/${modelId}/stats`)
    return response.data
  }

  // 对比多个模型
  async compareModels(proposalData: MultiModelProposalCreate, modelIds: number[]): Promise<ComparisonResponse> {
    const response = await api.post('/multi-model-proposals/compare', {
      ...proposalData,
      model_ids: modelIds
    })
    return response.data
  }
}

export default new MultiModelProposalService()
