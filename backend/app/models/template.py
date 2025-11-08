from sqlalchemy import Column, Integer, String, DateTime, Text, Enum, JSON
from datetime import datetime
import enum
from app.models.base import Base


class TemplateType(str, enum.Enum):
    """模板类型枚举"""

    PROPOSAL = "proposal"  # 方案模板
    QUOTATION = "quotation"  # 报价单模板
    CONTRACT = "contract"  # 合同模板
    PRESENTATION = "presentation"  # 演示文稿模板


class Template(Base):
    """模板模型"""

    __tablename__ = "templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    type = Column(Enum(TemplateType), nullable=False)
    description = Column(Text)

    # 模板内容
    content = Column(Text, nullable=False)

    # 模板变量定义
    variables = Column(JSON)  # 变量名、类型、描述等

    # 模板文件
    file_path = Column(String(500))  # 如果是Word/Excel模板文件

    # 元数据
    is_default = Column(Integer, default=0)  # 是否为默认模板
    is_active = Column(Integer, default=1)

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Template {self.name}>"
