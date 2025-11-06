from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.models import Template, TemplateType

router = APIRouter()

# Pydantic模型
class TemplateCreate(BaseModel):
    name: str
    type: TemplateType
    description: Optional[str] = None
    content: str
    variables: Optional[dict] = None


class TemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    content: Optional[str] = None
    variables: Optional[dict] = None


class TemplateResponse(BaseModel):
    id: int
    name: str
    type: TemplateType
    description: Optional[str]
    is_default: int
    is_active: int
    created_at: datetime

    class Config:
        from_attributes = True


class TemplateDetail(TemplateResponse):
    content: str
    variables: Optional[dict]


class TemplateList(BaseModel):
    total: int
    items: List[TemplateResponse]


@router.post("/", response_model=TemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_template(
    template_data: TemplateCreate,
    db: Session = Depends(get_db)
):
    """创建模板"""
    db_template = Template(
        name=template_data.name,
        type=template_data.type,
        description=template_data.description,
        content=template_data.content,
        variables=template_data.variables
    )

    db.add(db_template)
    db.commit()
    db.refresh(db_template)

    return db_template


@router.get("/", response_model=TemplateList)
async def list_templates(
    skip: int = 0,
    limit: int = 50,
    template_type: Optional[TemplateType] = None,
    db: Session = Depends(get_db)
):
    """获取模板列表"""
    query = db.query(Template).filter(Template.is_active == 1)

    if template_type:
        query = query.filter(Template.type == template_type)

    total = query.count()
    items = query.order_by(Template.is_default.desc(), Template.created_at.desc()).offset(skip).limit(limit).all()

    return {"total": total, "items": items}


@router.get("/{template_id}", response_model=TemplateDetail)
async def get_template(
    template_id: int,
    db: Session = Depends(get_db)
):
    """获取模板详情"""
    template = db.query(Template).filter(
        Template.id == template_id,
        Template.is_active == 1
    ).first()

    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")

    return template


@router.put("/{template_id}", response_model=TemplateDetail)
async def update_template(
    template_id: int,
    template_data: TemplateUpdate,
    db: Session = Depends(get_db)
):
    """更新模板"""
    template = db.query(Template).filter(Template.id == template_id).first()

    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")

    # 更新字段
    if template_data.name:
        template.name = template_data.name
    if template_data.description is not None:
        template.description = template_data.description
    if template_data.content:
        template.content = template_data.content
    if template_data.variables is not None:
        template.variables = template_data.variables

    db.commit()
    db.refresh(template)

    return template


@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_template(
    template_id: int,
    db: Session = Depends(get_db)
):
    """删除模板（软删除）"""
    template = db.query(Template).filter(Template.id == template_id).first()

    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")

    # 软删除
    template.is_active = 0
    db.commit()

    return None
