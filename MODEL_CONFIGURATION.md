# AI模型配置功能

系统现已支持多AI模型供应商配置，用户可以灵活配置和使用不同的AI模型来生成售前方案。

## 🎯 功能特性

### 1. 多供应商支持
- **OpenAI**: GPT-3.5, GPT-4, GPT-4-Turbo等
- **通义千问**: 阿里云大模型服务
- **文心一言**: 百度智能云模型
- **智谱AI**: GLM-4, GLM-3-Turbo等
- **DeepSeek**: 开源大模型API

### 2. 高级参数配置
- **基础配置**: API密钥、模型名称、基础URL
- **生成参数**: 温度、Top-P、频率惩罚、存在惩罚
- **限制参数**: 最大输出Token、上下文长度
- **超时配置**: 请求超时、最大重试次数
- **自定义参数**: 额外的请求头和模型参数

### 3. 模型管理
- **启用/禁用**: 灵活控制模型可用性
- **默认模型**: 设置系统默认使用的模型
- **测试连接**: 验证模型配置是否正确
- **统计信息**: 调用次数、成功率、Token消耗

### 4. 方案生成选择
- **单模型生成**: 选择特定模型生成方案
- **多模型对比**: 同时使用多个模型生成，对比效果
- **实时预览**: 生成前预览效果
- **性能监控**: 监控生成速度和质量

## 🛠️ 使用指南

### 1. 配置AI模型

访问 `AI模型配置` 页面：

1. **添加模型**
   ```typescript
   // 基本配置示例
   {
     name: "GPT-4",
     provider: "openai",
     model_name: "gpt-4",
     api_key: "sk-xxx...",
     temperature: 0.7,
     max_tokens: 4096
   }
   ```

2. **导入预设模型**
   - 系统提供常用模型的预设配置
   - 可直接导入并修改API密钥

3. **测试模型连接**
   - 发送测试请求验证配置
   - 查看响应时间和Token消耗

### 2. 多模型方案生成

访问 `方案生成 > 多模型生成`：

1. **填写方案信息**
   - 基本信息：标题、客户、需求等
   - 选择参考文档和模板

2. **选择生成模式**
   - **单模型**: 选择一个模型生成
   - **多模型对比**: 选择2-3个模型同时生成

3. **生成方案**
   - 实时查看生成进度
   - 对比不同模型的生成效果
   - 选择最佳结果保存

## 📊 模型性能对比

### 模型特性对比

| 模型 | 上下文长度 | 输出速度 | 成本 | 适合场景 |
|------|------------|----------|------|----------|
| GPT-4 | 8K | 中等 | 高 | 复杂推理、长文本 |
| GPT-3.5 | 16K | 快 | 中 | 通用生成、快速响应 |
| 通义千问 | 8K | 快 | 中 | 中文理解、本地化 |
| 文心一言 | 4K | 中等 | 中 | 中文处理、行业知识 |
| GLM-4 | 128K | 中等 | 中 | 长文档处理、上下文 |
| DeepSeek | 16K | 快 | 低 | 成本敏感、快速原型 |

### 生成质量评估

系统提供多维度质量评估：

1. **内容完整性**
   - 结构完整性
   - 要素覆盖度
   - 逻辑连贯性

2. **技术准确性**
   - 术语准确性
   - 技术深度
   - 可行性分析

3. **商业价值**
   - 方案创新性
   - 成本效益
   - 风险评估

## 🔧 配置示例

### OpenAI GPT-4配置
```json
{
  "name": "OpenAI GPT-4",
  "provider": "openai",
  "model_name": "gpt-4",
  "api_key": "sk-proj-xxx...",
  "base_url": "https://api.openai.com/v1",
  "max_tokens": 4096,
  "context_length": 8192,
  "temperature": 0.7,
  "top_p": 1.0,
  "frequency_penalty": 0.0,
  "presence_penalty": 0.0,
  "timeout": 120,
  "max_retries": 3,
  "description": "OpenAI GPT-4模型，适合复杂推理",
  "is_enabled": true,
  "is_default": false
}
```

### 通义千问配置
```json
{
  "name": "通义千问-Plus",
  "provider": "tongyi",
  "model_name": "qwen-plus",
  "api_key": "sk-xxx...",
  "base_url": "https://dashscope.aliyuncs.com/api/v1",
  "max_tokens": 2000,
  "context_length": 8192,
  "temperature": 0.7,
  "description": "阿里云通义千问Plus模型",
  "is_enabled": true
}
```

### 智谱GLM-4配置
```json
{
  "name": "智谱GLM-4",
  "provider": "zhipu",
  "model_name": "glm-4",
  "api_key": "xxx...",
  "base_url": "https://open.bigmodel.cn/api/paas/v4",
  "max_tokens": 4096,
  "context_length": 128000,
  "temperature": 0.7,
  "description": "智谱AI GLM-4长上下文模型",
  "is_enabled": true
}
```

## 🚀 API使用

### 1. 模型配置API

```bash
# 获取所有模型
GET /api/ai/models

# 创建模型配置
POST /api/ai/models
{
  "name": "Custom Model",
  "provider": "openai",
  "model_name": "gpt-3.5-turbo",
  ...
}

# 测试模型连接
POST /api/ai/models/{id}/test
{
  "prompt": "请简单介绍一下你自己"
}
```

### 2. 多模型方案生成API

```bash
# 获取可用模型
GET /api/multi-model-proposals/models/available

# 使用指定模型生成方案
POST /api/multi-model-proposals/generate
{
  "title": "银行风控方案",
  "customer_name": "某某银行",
  "requirements": "构建实时风控系统",
  "model_id": 1
}

# 对比多个模型
POST /api/multi-model-proposals/compare
{
  "title": "银行风控方案",
  "requirements": "构建实时风控系统",
  "model_ids": [1, 2, 3]
}
```

## 📈 性能监控

### 统计指标
- **调用次数**: 总调用次数和成功次数
- **响应时间**: 平均响应时间和P95延迟
- **Token消耗**: 输入和输出Token统计
- **成功率**: 模型生成成功率

### 监控告警
- **模型故障**: 连接失败或API错误
- **性能下降**: 响应时间异常
- **用量超限**: Token消耗接近限额

## 🎨 前端界面

### 1. 模型配置页面
- 模型列表展示
- 添加/编辑/删除模型
- 测试模型连接
- 预设模型导入

### 2. 多模型生成页面
- 分步骤引导
- 模型选择界面
- 实时生成预览
- 对比结果展示

### 3. 性能统计页面
- 模型使用统计
- 性能趋势图表
- 成本分析报告

## 🔮 未来规划

### 1. 智能模型推荐
- 基于需求类型推荐最适合的模型
- 考虑成本、速度、质量等因素
- 自适应优化模型选择

### 2. 模型微调
- 支持用户自定义模型微调
- 行业知识定制化训练
- 个性化生成风格

### 3. 混合生成
- 多模型协同生成
- 分阶段使用不同模型
- 质量和成本平衡

## 📋 最佳实践

### 1. 模型选择建议
- **复杂方案**: GPT-4, GLM-4
- **快速原型**: GPT-3.5, DeepSeek
- **中文优化**: 通义千问, 文心一言
- **长文档**: GLM-4 (128K上下文)

### 2. 参数调优
- **创意需求**: 温度 0.8-1.0
- **严谨文档**: 温度 0.3-0.5
- **平衡方案**: 温度 0.6-0.8
- **控制输出**: 调整惩罚参数

### 3. 成本控制
- 优先使用性价比高的模型
- 合理设置Token限制
- 监控使用量变化
- 定期评估模型效果

---

💡 **提示**: 系统支持快速切换模型，建议根据具体需求选择最适合的模型配置。首次使用建议导入预设模型并配置API密钥后进行测试。
