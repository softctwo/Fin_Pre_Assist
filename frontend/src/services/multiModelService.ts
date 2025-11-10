import api from './api'

export interface ModelInfo {
  provider: string
  name: string
  model: string
  available: boolean
}

export interface ProposalGenerationRequest {
  proposalId: number
  selectedModels: string[]
  requirements?: string
  iterationFeedback?: string
  parent_version_id?: number
}

export interface ProposalIterationRequest {
  versionId: number
  feedback: string
  selectedModels: string[]
}

export interface VersionComparisonRequest {
  versionIds: number[]
}

export const multiModelService = {
  // 获取可用模型列表
  async getAvailableModels(): Promise<ModelInfo[]> {
    const response = await api.get('/multi-model/models')
    return response.data
  },

  // 生成方案版本
  async generateProposalVersions(data: ProposalGenerationRequest): Promise<void> {
    return api.post('/multi-model/generate-versions', data)
  },

  // 迭代方案版本
  async iterateProposalVersion(data: ProposalIterationRequest): Promise<void> {
    return api.post('/multi-model/iterate-version', data)
  },

  // 获取方案版本列表
  async getProposalVersions(proposalId: number): Promise<any[]> {
    return api.get(`/multi-model/proposals/${proposalId}/versions`)
  },

  // 获取版本详情
  async getProposalVersion(versionId: number): Promise<any> {
    return api.get(`/multi-model/versions/${versionId}`)
  },

  // 对比版本
  async compareVersions(versionIds: number[]): Promise<any> {
    return api.post('/multi-model/compare-versions', { version_ids: versionIds })
  },

  // 为版本评分
  async rateVersion(versionId: number, rating: number): Promise<any> {
    return api.post(`/multi-model/versions/${versionId}/rate`, null, {
      params: { rating }
    })
  },

  // 选定版本
  async selectVersion(versionId: number): Promise<any> {
    return api.post(`/multi-model/versions/${versionId}/select`)
  }
}