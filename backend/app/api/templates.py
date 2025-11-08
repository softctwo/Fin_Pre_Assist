from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.models import Template, TemplateType, User
from app.api.auth import get_current_active_user
from app.services.template_service import template_service

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

    model_config = ConfigDict(from_attributes=True)


class TemplateDetail(TemplateResponse):
    content: str
    variables: Optional[dict]


class TemplateList(BaseModel):
    total: int
    items: List[TemplateResponse]


@router.post("/", response_model=TemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_template(
    template_data: TemplateCreate,
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_active_user),
):
    """创建模板"""
    db_template = Template(
        name=template_data.name,
        type=template_data.type,
        description=template_data.description,
        content=template_data.content,
        variables=template_data.variables,
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
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_active_user),
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
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_active_user),
):
    """获取模板详情"""
    template = db.query(Template).filter(Template.id == template_id, Template.is_active == 1).first()

    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")

    return template


@router.put("/{template_id}", response_model=TemplateDetail)
async def update_template(
    template_id: int,
    template_data: TemplateUpdate,
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_active_user),
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
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_active_user),
):
    """删除模板（软删除）"""
    template = db.query(Template).filter(Template.id == template_id).first()

    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")

    # 软删除
    template.is_active = 0
    db.commit()

    return None


@router.post("/{template_id}/preview")
async def preview_template(
    template_id: int,
    sample_data: dict,
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_active_user),
):
    """预览模板渲染效果"""
    template = db.query(Template).filter(Template.id == template_id).first()

    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")

    try:
        preview_content = template_service.preview_template(template.content, sample_data)
        return {"preview": preview_content}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"预览失败: {str(e)}")


@router.get("/{template_id}/variables")
async def get_template_variables(
    template_id: int,
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_active_user),
):
    """提取模板中的所有变量"""
    template = db.query(Template).filter(Template.id == template_id).first()

    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")

    variables = template_service.extract_variables(template.content)
    default_vars = template_service.get_default_variables()

    return {"variables": variables, "default_values": default_vars}


class TemplateValidationRequest(BaseModel):
    content: str


@router.post("/validate")
async def validate_template_syntax(
    request: TemplateValidationRequest,
    _current_user: User = Depends(get_current_active_user),
):
    """验证模板语法"""
    from app.services.template_service import template_service

    is_valid, error_msg = template_service.validate_template(request.content)

    if is_valid:
        return {"valid": True, "message": "模板语法正确"}
    else:
        return {"valid": False, "error": error_msg}
