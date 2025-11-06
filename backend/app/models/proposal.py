from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.core.database import Base


class ProposalStatus(str, enum.Enum):
    """方案状态枚举"""
    DRAFT = "draft"           # 草稿
    GENERATING = "generating" # 生成中
    COMPLETED = "completed"   # 已完成
    EXPORTED = "exported"     # 已导出
    ARCHIVED = "archived"     # 已归档


class Proposal(Base):
    """方案模型"""
    __tablename__ = "proposals"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)

    # 客户信息
    customer_name = Column(String(200), nullable=False)
    customer_industry = Column(String(100))
    customer_contact = Column(String(100))

    # 需求信息
    requirements = Column(Text)  # 客户需求描述
    requirements_structured = Column(JSON)  # 结构化需求

    # 生成的内容
    executive_summary = Column(Text)  # 执行摘要
    solution_overview = Column(Text)  # 解决方案概述
    technical_details = Column(Text)  # 技术细节
    implementation_plan = Column(Text)  # 实施计划
    pricing = Column(JSON)  # 报价信息

    # 完整内容
    full_content = Column(Text)  # 完整方案内容

    # 参考文档
    reference_documents = Column(JSON)  # 参考的历史文档ID列表

    # 状态
    status = Column(Enum(ProposalStatus), default=ProposalStatus.DRAFT)

    # 元数据
    metadata = Column(JSON)

    # 关联
    user_id = Column(Integer, ForeignKey("users.id"))

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    user = relationship("User", back_populates="proposals")

    def __repr__(self):
        return f"<Proposal {self.title}>"
