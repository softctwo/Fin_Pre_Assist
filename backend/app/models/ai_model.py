"""AI模型配置数据模型"""

from sqlalchemy import Column, Integer, String, Boolean, Float, JSON, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class AIModel(Base):
    """AI模型配置表"""
    __tablename__ = "ai_models"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="模型显示名称")
    provider = Column(String(50), nullable=False, comment="模型供应商")
    model_name = Column(String(100), nullable=False, comment="模型名称")
    
    # 连接配置
    api_key = Column(String(500), nullable=True, comment="API密钥")
    base_url = Column(String(500), nullable=True, comment="API基础URL")
    
    # 模型参数配置
    max_tokens = Column(Integer, default=2000, comment="最大输出Token数")
    context_length = Column(Integer, default=4096, comment="上下文长度")
    temperature = Column(Float, default=0.7, comment="生成温度")
    top_p = Column(Float, default=1.0, comment="Top-P采样")
    frequency_penalty = Column(Float, default=0.0, comment="频率惩罚")
    presence_penalty = Column(Float, default=0.0, comment="存在惩罚")
    
    # 高级配置
    timeout = Column(Integer, default=120, comment="请求超时时间(秒)")
    max_retries = Column(Integer, default=3, comment="最大重试次数")
    headers = Column(Text, nullable=True, comment="自定义请求头")
    extra_params = Column(Text, nullable=True, comment="额外参数")
    
    # 状态和描述
    is_enabled = Column(Boolean, default=True, comment="是否启用")
    is_default = Column(Boolean, default=False, comment="是否为默认模型")
    description = Column(Text, nullable=True, comment="模型描述")
    
    # 统计信息
    total_calls = Column(Integer, default=0, comment="总调用次数")
    success_calls = Column(Integer, default=0, comment="成功调用次数")
    total_tokens = Column(Integer, default=0, comment="总Token消耗")
    
    # 元数据
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), comment="更新时间")
    
    def __repr__(self):
        return f"<AIModel(id={self.id}, name='{self.name}', provider='{self.provider}')>"
    
    @property
    def success_rate(self) -> float:
        """成功率"""
        if self.total_calls == 0:
            return 0.0
        return (self.success_calls / self.total_calls) * 100
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            "id": self.id,
            "name": self.name,
            "provider": self.provider,
            "model_name": self.model_name,
            "api_key": self.api_key,
            "base_url": self.base_url,
            "max_tokens": self.max_tokens,
            "context_length": self.context_length,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "frequency_penalty": self.frequency_penalty,
            "presence_penalty": self.presence_penalty,
            "timeout": self.timeout,
            "max_retries": self.max_retries,
            "headers": self.headers,
            "extra_params": self.extra_params,
            "is_enabled": self.is_enabled,
            "is_default": self.is_default,
            "description": self.description,
            "total_calls": self.total_calls,
            "success_calls": self.success_calls,
            "total_tokens": self.total_tokens,
            "success_rate": self.success_rate,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


# 预设的模型配置模板
PRESET_MODEL_CONFIGS = [
    {
        "name": "GPT-3.5-Turbo",
        "provider": "openai",
        "model_name": "gpt-3.5-turbo",
        "base_url": "https://api.openai.com/v1",
        "max_tokens": 4096,
        "context_length": 16385,
        "temperature": 0.7,
        "description": "OpenAI的GPT-3.5 Turbo模型，适合通用文本生成任务"
    },
    {
        "name": "GPT-4",
        "provider": "openai",
        "model_name": "gpt-4",
        "base_url": "https://api.openai.com/v1",
        "max_tokens": 8192,
        "context_length": 8192,
        "temperature": 0.7,
        "description": "OpenAI的GPT-4模型，更强大的推理能力"
    },
    {
        "name": "通义千问-Plus",
        "provider": "tongyi",
        "model_name": "qwen-plus",
        "base_url": "https://dashscope.aliyuncs.com/api/v1",
        "max_tokens": 2000,
        "context_length": 8192,
        "temperature": 0.7,
        "description": "阿里云通义千问Plus模型，中文理解能力强"
    },
    {
        "name": "文心一言-Turbo",
        "provider": "wenxin",
        "model_name": "ernie-bot-turbo",
        "base_url": "https://aip.baidubce.com/rpc/2.0/ai_custom/v1",
        "max_tokens": 2048,
        "context_length": 4096,
        "temperature": 0.7,
        "description": "百度文心一言Turbo模型，响应速度快"
    },
    {
        "name": "智谱GLM-4",
        "provider": "zhipu",
        "model_name": "glm-4",
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "max_tokens": 4096,
        "context_length": 128000,
        "temperature": 0.7,
        "description": "智谱AI的GLM-4模型，支持长上下文"
    },
    {
        "name": "DeepSeek-Chat",
        "provider": "deepseek",
        "model_name": "deepseek-chat",
        "base_url": "https://api.deepseek.com/v1",
        "max_tokens": 4096,
        "context_length": 16385,
        "temperature": 0.7,
        "description": "DeepSeek的聊天模型，性价比高"
    }
]
