from sqlalchemy import Column, Integer, String, DateTime, Text, JSON
from datetime import datetime
from app.core.database import Base


class KnowledgeBase(Base):
    """知识库模型"""
    __tablename__ = "knowledge_base"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(100), nullable=False, index=True)  # 分类：产品、解决方案、案例等
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)

    # 标签
    tags = Column(JSON)  # 标签列表

    # 元数据
    metadata = Column(JSON)

    # 向量化
    is_vectorized = Column(Integer, default=0)
    vector_id = Column(String(100))

    # 权重（用于搜索排序）
    weight = Column(Integer, default=1)

    # 状态
    is_active = Column(Integer, default=1)

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<KnowledgeBase {self.title}>"
