from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum, JSON, Index
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.core.database import Base


class DocumentType(str, enum.Enum):
    """文档类型枚举"""
    TECHNICAL_PROPOSAL = "technical_proposal"  # 技术方案
    BUSINESS_PROPOSAL = "business_proposal"    # 商务方案
    QUOTATION = "quotation"                    # 报价单
    BID_DOCUMENT = "bid_document"              # 投标文档
    CASE_STUDY = "case_study"                  # 案例
    OTHER = "other"                            # 其他


class Document(Base):
    """文档模型"""
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)  # 添加索引支持文档名搜索
    type = Column(Enum(DocumentType), nullable=False, index=True)  # 添加索引支持类型筛选
    file_path = Column(String(500), nullable=False)
    file_name = Column(String(200), nullable=False)
    file_size = Column(Integer)  # 文件大小（字节）
    mime_type = Column(String(100))

    # 文档内容
    content_text = Column(Text)  # 提取的文本内容

    # 元数据
    doc_metadata = Column(JSON)  # 存储额外的元数据

    # 分类标签
    industry = Column(String(100), index=True)  # 行业 - 添加索引
    customer_name = Column(String(200), index=True)  # 客户名称 - 添加索引
    tags = Column(JSON)  # 标签列表

    # 向量化标识
    is_vectorized = Column(Integer, default=0, index=True)  # 是否已向量化 - 添加索引
    vector_id = Column(String(100), index=True)  # 向量数据库中的ID - 添加索引

    # 关联
    user_id = Column(Integer, ForeignKey("users.id"))

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    user = relationship("User", back_populates="documents")
    
    # 复合索引 - 优化常用查询
    __table_args__ = (
        # 用户的文档列表查询（按类型和时间排序）
        Index('ix_document_user_type_created', 'user_id', 'type', 'created_at'),
        # 客户名和行业组合查询
        Index('ix_document_customer_industry', 'customer_name', 'industry'),
        # 向量化状态查询（用于批量处理）
        Index('ix_document_vectorized_created', 'is_vectorized', 'created_at'),
    )

    def __repr__(self):
        return f"<Document {self.title}>"
