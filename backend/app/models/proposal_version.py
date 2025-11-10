from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON, Index, UniqueConstraint, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum
from app.models.base import Base


class ProposalVersionStatus(str, Enum):
    DRAFT = "draft"  # 草稿
    GENERATING = "generating"  # 生成中
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"  # 生成失败
    SELECTED = "selected"  # 已选中


class ProposalVersion(Base):
    """方案版本模型

    记录方案的历史版本，支持版本回溯和比较。
    """

    __tablename__ = "proposal_versions"

    id = Column(Integer, primary_key=True, index=True)

    # 关联方案
    proposal_id = Column(Integer, ForeignKey("proposals.id"), nullable=False, index=True)

    # 版本信息
    version_number = Column(Integer, nullable=False)  # 版本号（1, 2, 3...）

    # 快照内容
    title = Column(String(200), nullable=False)
    customer_name = Column(String(200))
    customer_industry = Column(String(100))
    customer_contact = Column(String(100))

    # 完整内容快照（JSON格式）
    content = Column(JSON, nullable=False)  # 存储完整的方案内容
    """
    content结构示例：
    {
        "requirements": "...",
        "requirements_structured": {...},
        "executive_summary": "...",
        "solution_overview": "...",
        "technical_details": "...",
        "implementation_plan": "...",
        "pricing": {...},
        "full_content": "..."
    }
    """

    # 变更信息
    changes_summary = Column(Text)  # 变更摘要（可选）
    change_type = Column(String(50))  # 变更类型：manual（手动）、auto（自动）、major（重大变更）

    # AI模型相关字段
    model_provider = Column(String(50), nullable=False)  # AI模型提供商 (kimi, zhipu, deepseek等)
    model_name = Column(String(100), nullable=False)  # 模型名称
    status = Column(SQLEnum(ProposalVersionStatus), default=ProposalVersionStatus.DRAFT)

    # 迭代相关字段
    parent_version_id = Column(Integer, ForeignKey("proposal_versions.id"), nullable=True)  # 父版本ID
    iteration_feedback = Column(Text, nullable=True)  # 用户反馈
    iteration_prompt = Column(Text, nullable=True)  # 迭代时的完整提示

    # 生成统计信息
    generation_time = Column(DateTime, nullable=True)  # 生成完成时间
    generation_duration = Column(Integer, nullable=True)  # 生成耗时(秒)
    tokens_used = Column(Integer, nullable=True)  # 使用的token数

    # 评分字段
    quality_score = Column(Integer, nullable=True)  # 质量评分(1-10)
    user_rating = Column(Integer, nullable=True)  # 用户评分(1-5)

    # 创建信息
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # 元数据
    metadata_info = Column(JSON)  # 额外的元数据信息

    # 复合唯一约束：同一方案的版本号唯一
    __table_args__ = (
        UniqueConstraint("proposal_id", "version_number", name="uq_proposal_version"),
        # 索引优化
        Index("ix_version_proposal_created", "proposal_id", "created_at"),
        Index("ix_version_created", "created_at"),
    )

    # 关系
    proposal = relationship("Proposal", back_populates="versions")
    creator = relationship("User")
    parent_version = relationship("ProposalVersion", remote_side=[id])
    child_versions = relationship("ProposalVersion", remote_side=[parent_version_id])

    def __repr__(self):
        return f"<ProposalVersion {self.proposal_id} v{self.version_number}>"

    def to_dict(self):
        """转换为字典格式"""
        return {
            "id": self.id,
            "proposal_id": self.proposal_id,
            "version_number": self.version_number,
            "title": self.title,
            "customer_name": self.customer_name,
            "customer_industry": self.customer_industry,
            "customer_contact": self.customer_contact,
            "content": self.content,
            "changes_summary": self.changes_summary,
            "change_type": self.change_type,

            # AI模型相关
            "model_provider": self.model_provider,
            "model_name": self.model_name,
            "status": self.status.value if self.status else None,

            # 迭代相关
            "parent_version_id": self.parent_version_id,
            "iteration_feedback": self.iteration_feedback,
            "iteration_prompt": self.iteration_prompt,

            # 生成统计
            "generation_time": self.generation_time.isoformat() if self.generation_time else None,
            "generation_duration": self.generation_duration,
            "tokens_used": self.tokens_used,

            # 评分
            "quality_score": self.quality_score,
            "user_rating": self.user_rating,

            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "metadata_info": self.metadata_info,
        }

    def to_summary_dict(self):
        """转换为摘要格式（不包含完整内容）"""
        return {
            "id": self.id,
            "proposal_id": self.proposal_id,
            "version_number": self.version_number,
            "title": self.title,
            "changes_summary": self.changes_summary,
            "change_type": self.change_type,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
