import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import metricsService, { getMetricsSummary, type MetricsSummary } from '../metricsService'
import api from '../api'

// Mock API module
vi.mock('../api', () => ({
  default: {
    get: vi.fn()
  }
}))

const mockApi = api as any

describe.skip('MetricsService Comprehensive Tests', () => {
  const mockMetricsSummary: MetricsSummary = {
    documents: 42,
    proposals: 15,
    cache_hit_rate: '85.5%',
    cache_type: 'redis',
    cache_keys: 128,
    ai_provider: 'openai',
    ai_calls: 234,
    ai_tokens: 15678,
    vector_searches: 89
  }

  const mockSystemMetrics = {
    cpu_usage: '45.2%',
    memory_usage: '67.8%',
    disk_usage: '82.1%',
    uptime: '72h 15m',
    active_connections: 15
  }

  const mockUserActivityMetrics = {
    active_users: 12,
    total_logins: 456,
    average_session_duration: '45m 32s',
    peak_usage_time: '14:30',
    new_users_today: 3
  }

  const mockApiMetrics = {
    total_requests: 1234,
    average_response_time: '245ms',
    error_rate: '2.1%',
    slow_requests: 23,
    endpoints: {
      '/api/v1/auth/login': { requests: 156, avg_time: '120ms' },
      '/api/v1/proposals': { requests: 89, avg_time: '340ms' }
    }
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('getMetricsSummary 函数测试', () => {
    it('应该成功获取指标摘要', async () => {
      mockApi.get.mockResolvedValue({ data: mockMetricsSummary })

      const result = await getMetricsSummary()

      expect(mockApi.get).toHaveBeenCalledWith('/metrics/summary')
      expect(result).toEqual(mockMetricsSummary)
      expect(result.documents).toBe(42)
      expect(result.proposals).toBe(15)
      expect(result.cache_hit_rate).toBe('85.5%')
    })

    it('应该处理API错误', async () => {
      const mockError = new Error('Network error')
      mockApi.get.mockRejectedValue(mockError)

      await expect(getMetricsSummary()).rejects.toThrow('Network error')
      expect(mockApi.get).toHaveBeenCalledWith('/metrics/summary')
    })

    it('应该处理空响应', async () => {
      mockApi.get.mockResolvedValue({ data: null })

      const result = await getMetricsSummary()

      expect(result).toBeNull()
    })

    it('应该处理部分数据', async () => {
      const partialData = {
        documents: 10,
        proposals: 5
        // 缺少其他字段
      }
      mockApi.get.mockResolvedValue({ data: partialData })

      const result = await getMetricsSummary()

      expect(result).toEqual(partialData)
      expect(result.documents).toBe(10)
      expect(result.proposals).toBe(5)
    })
  })

  describe('metricsService.getMetricsSummary 方法测试', () => {
    it('应该正确调用 getMetricsSummary', async () => {
      mockApi.get.mockResolvedValue({ data: mockMetricsSummary })

      const result = await metricsService.getMetricsSummary()

      expect(result).toEqual(mockMetricsSummary)
      expect(mockApi.get).toHaveBeenCalledWith('/metrics/summary')
    })
  })

  describe('metricsService.getSystemMetrics 方法测试', () => {
    it('应该成功获取系统指标', async () => {
      mockApi.get.mockResolvedValue({ data: mockSystemMetrics })

      const result = await metricsService.getSystemMetrics()

      expect(mockApi.get).toHaveBeenCalledWith('/metrics/system')
      expect(result).toEqual(mockSystemMetrics)
      expect(result.cpu_usage).toBe('45.2%')
      expect(result.memory_usage).toBe('67.8%')
      expect(result.active_connections).toBe(15)
    })

    it('应该处理系统指标API错误', async () => {
      const mockError = new Error('Server error')
      mockApi.get.mockRejectedValue(mockError)

      await expect(metricsService.getSystemMetrics()).rejects.toThrow('Server error')
      expect(mockApi.get).toHaveBeenCalledWith('/metrics/system')
    })
  })

  describe('metricsService.getUserActivityMetrics 方法测试', () => {
    it('应该成功获取用户活动指标', async () => {
      mockApi.get.mockResolvedValue({ data: mockUserActivityMetrics })

      const result = await metricsService.getUserActivityMetrics()

      expect(mockApi.get).toHaveBeenCalledWith('/metrics/user-activity')
      expect(result).toEqual(mockUserActivityMetrics)
      expect(result.active_users).toBe(12)
      expect(result.total_logins).toBe(456)
      expect(result.new_users_today).toBe(3)
    })

    it('应该处理用户活动指标API错误', async () => {
      const mockError = new Error('Database error')
      mockApi.get.mockRejectedValue(mockError)

      await expect(metricsService.getUserActivityMetrics()).rejects.toThrow('Database error')
      expect(mockApi.get).toHaveBeenCalledWith('/metrics/user-activity')
    })
  })

  describe('metricsService.getApiMetrics 方法测试', () => {
    it('应该成功获取API指标', async () => {
      mockApi.get.mockResolvedValue({ data: mockApiMetrics })

      const result = await metricsService.getApiMetrics()

      expect(mockApi.get).toHaveBeenCalledWith('/metrics/api')
      expect(result).toEqual(mockApiMetrics)
      expect(result.total_requests).toBe(1234)
      expect(result.average_response_time).toBe('245ms')
      expect(result.error_rate).toBe('2.1%')
      expect(result.endpoints['/api/v1/auth/login'].requests).toBe(156)
    })

    it('应该处理API指标错误', async () => {
      const mockError = new Error('Metrics service unavailable')
      mockApi.get.mockRejectedValue(mockError)

      await expect(metricsService.getApiMetrics()).rejects.toThrow('Metrics service unavailable')
      expect(mockApi.get).toHaveBeenCalledWith('/metrics/api')
    })
  })

  describe('错误处理边界测试', () => {
    it('应该处理网络超时', async () => {
      const timeoutError = new Error('Network timeout')
      timeoutError.name = 'TimeoutError'
      mockApi.get.mockRejectedValue(timeoutError)

      await expect(metricsService.getMetricsSummary()).rejects.toThrow('Network timeout')
    })

    it('应该处理HTTP错误状态', async () => {
      const httpError = new Error('Internal Server Error')
      ;(httpError as any).response = { status: 500, data: { message: 'Internal error' } }
      mockApi.get.mockRejectedValue(httpError)

      await expect(metricsService.getMetricsSummary()).rejects.toThrow('Internal Server Error')
    })

    it('应该处理空响应数据', async () => {
      mockApi.get.mockResolvedValue({})

      const result = await metricsService.getMetricsSummary()

      expect(result).toBeUndefined()
    })

    it('应该处理undefined响应', async () => {
      mockApi.get.mockResolvedValue(undefined)

      const result = await metricsService.getMetricsSummary()

      expect(result).toBeUndefined()
    })
  })

  describe('数据验证测试', () => {
    it('应该验证返回数据的结构', async () => {
      mockApi.get.mockResolvedValue({ data: mockMetricsSummary })

      const result = await metricsService.getMetricsSummary()

      // 验证必需字段
      expect(result).toHaveProperty('documents')
      expect(result).toHaveProperty('proposals')
      expect(result).toHaveProperty('cache_hit_rate')
      expect(result).toHaveProperty('ai_calls')
      expect(result).toHaveProperty('ai_tokens')

      // 验证数据类型
      expect(typeof result.documents).toBe('number')
      expect(typeof result.proposals).toBe('number')
      expect(typeof result.cache_hit_rate).toBe('string')
      expect(typeof result.ai_calls).toBe('number')
      expect(typeof result.ai_tokens).toBe('number')
    })

    it('应该处理负数值', async () => {
      const negativeData = {
        ...mockMetricsSummary,
        documents: -5,
        ai_calls: -10
      }
      mockApi.get.mockResolvedValue({ data: negativeData })

      const result = await metricsService.getMetricsSummary()

      expect(result.documents).toBe(-5)
      expect(result.ai_calls).toBe(-10)
    })

    it('应该处理零值', async () => {
      const zeroData = {
        documents: 0,
        proposals: 0,
        cache_hit_rate: '0%',
        cache_keys: 0,
        ai_calls: 0,
        ai_tokens: 0,
        vector_searches: 0
      }
      mockApi.get.mockResolvedValue({ data: zeroData })

      const result = await metricsService.getMetricsSummary()

      expect(result.documents).toBe(0)
      expect(result.ai_calls).toBe(0)
      expect(result.cache_hit_rate).toBe('0%')
    })
  })

  describe('性能测试', () => {
    it('应该处理大量数据', async () => {
      const largeData = {
        ...mockMetricsSummary,
        documents: 999999,
        proposals: 999999,
        ai_calls: 999999,
        ai_tokens: 999999999
      }
      mockApi.get.mockResolvedValue({ data: largeData })

      const result = await metricsService.getMetricsSummary()

      expect(result.documents).toBe(999999)
      expect(result.ai_calls).toBe(999999)
      expect(result.ai_tokens).toBe(999999999)
    })

    it('应该处理浮点数', async () => {
      const floatData = {
        ...mockMetricsSummary,
        cache_hit_rate: '85.12345%'
      }
      mockApi.get.mockResolvedValue({ data: floatData })

      const result = await metricsService.getMetricsSummary()

      expect(result.cache_hit_rate).toBe('85.12345%')
    })
  })

  describe('并发测试', () => {
    it('应该处理并发请求', async () => {
      mockApi.get
        .mockResolvedValueOnce({ data: mockMetricsSummary })
        .mockResolvedValueOnce({ data: mockSystemMetrics })
        .mockResolvedValueOnce({ data: mockUserActivityMetrics })
        .mockResolvedValueOnce({ data: mockApiMetrics })

      const results = await Promise.all([
        metricsService.getMetricsSummary(),
        metricsService.getSystemMetrics(),
        metricsService.getUserActivityMetrics(),
        metricsService.getApiMetrics()
      ])

      expect(results[0]).toEqual(mockMetricsSummary)
      expect(results[1]).toEqual(mockSystemMetrics)
      expect(results[2]).toEqual(mockUserActivityMetrics)
      expect(results[3]).toEqual(mockApiMetrics)

      expect(mockApi.get).toHaveBeenCalledTimes(4)
    })
  })

  describe('类型安全测试', () => {
    it('应该保持类型安全', async () => {
      mockApi.get.mockResolvedValue({ data: mockMetricsSummary })

      const result = await getMetricsSummary()

      // TypeScript编译时检查
      const checkType = (data: MetricsSummary): void => {
        expect(typeof data.documents).toBe('number')
        expect(typeof data.cache_hit_rate).toBe('string')
      }

      checkType(result)
    })
  })
})
