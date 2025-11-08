from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime
import os
import uuid
import shutil

from app.core.database import get_db
from app.core.config import settings
from app.models import Document, DocumentType, User
from app.api.auth import get_current_active_user
from app.services.document_processor import DocumentProcessor
from app.services.vector_service import vector_service
from loguru import logger

router = APIRouter()


# Pydantic模型
class DocumentResponse(BaseModel):
    id: int
    title: str
    type: DocumentType
    file_name: str
    file_size: Optional[int]
    industry: Optional[str]
    customer_name: Optional[str]
    tags: Optional[list]
    is_vectorized: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DocumentList(BaseModel):
    total: int
    items: List[DocumentResponse]


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    doc_type: DocumentType = Form(...),
    industry: Optional[str] = Form(None),
    customer_name: Optional[str] = Form(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """上传文档"""
    # 检查文件大小
    file.file.seek(0, 2)  # 移到文件末尾
    file_size = file.file.tell()
    file.file.seek(0)  # 回到文件开头

    if file_size > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"文件大小超过限制 ({settings.MAX_UPLOAD_SIZE} bytes)",
        )

    # 检查文件类型
    allowed_extensions = [".doc", ".docx", ".pdf", ".txt", ".xls", ".xlsx"]
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的文件类型。支持的类型: {', '.join(allowed_extensions)}",
        )

    # 生成唯一文件名
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)

    # 保存文件
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"文件保存失败: {str(e)}")

    # 创建数据库记录
    db_document = Document(
        title=title,
        type=doc_type,
        file_path=file_path,
        file_name=file.filename,
        file_size=file_size,
        mime_type=file.content_type,
        industry=industry,
        customer_name=customer_name,
        user_id=current_user.id,
    )

    db.add(db_document)
    db.commit()
    db.refresh(db_document)

    # 提取文本并向量化
    try:
        # 提取文本
        text_content = DocumentProcessor.extract_text(file_path)
        db_document.content_text = text_content

        # 向量化
        vector_id = vector_service.add_document(
            doc_id=db_document.id,
            title=title,
            content=text_content,
            metadata={
                "type": doc_type.value,
                "industry": industry,
                "customer_name": customer_name,
            },
        )

        db_document.vector_id = vector_id
        db_document.is_vectorized = 1

        db.commit()
        db.refresh(db_document)

        logger.info(f"文档 {db_document.id} 处理完成")

    except Exception as e:
        logger.error(f"文档处理失败: {e}")
        # 即使处理失败，文档记录仍然保存

    return db_document


@router.get("/", response_model=DocumentList)
async def list_documents(
    skip: int = 0,
    limit: int = 20,
    doc_type: Optional[DocumentType] = None,
    industry: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取文档列表"""
    query = db.query(Document).filter(Document.user_id == current_user.id)

    if doc_type:
        query = query.filter(Document.type == doc_type)
    if industry:
        query = query.filter(Document.industry == industry)

    total = query.count()
    items = query.order_by(Document.created_at.desc()).offset(skip).limit(limit).all()

    return {"total": total, "items": items}


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: int, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)
):
    """获取文档详情"""
    document = db.query(Document).filter(Document.id == document_id, Document.user_id == current_user.id).first()

    if not document:
        raise HTTPException(status_code=404, detail="文档不存在")

    return document


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: int, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)
):
    """删除文档"""
    document = db.query(Document).filter(Document.id == document_id, Document.user_id == current_user.id).first()

    if not document:
        raise HTTPException(status_code=404, detail="文档不存在")

    # 删除向量数据
    if document.vector_id:
        try:
            vector_service.delete_document(document.vector_id, doc_id=document.id)
        except Exception as e:
            logger.error(f"删除向量数据失败: {e}")

    # 删除物理文件
    try:
        if os.path.exists(document.file_path):
            os.remove(document.file_path)
    except Exception as e:
        logger.error(f"删除文件失败: {e}")

    # 删除数据库记录
    db.delete(document)
    db.commit()

    return None
