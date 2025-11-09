from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime
from loguru import logger

from app.core.database import get_db
from app.models import Proposal, ProposalStatus, User
from app.api.auth import get_current_active_user
from app.services.proposal_generator import ProposalGenerator
from app.services.export_service import export_service
from app.services.cache_service import cache_service
from app.utils.security_utils import sanitize_for_api
from fastapi.responses import FileResponse

router = APIRouter()


# Pydantic模型
class ProposalCreate(BaseModel):
    title: str
    customer_name: str
    customer_industry: Optional[str] = None
    customer_contact: Optional[str] = None
    requirements: str
    reference_document_ids: Optional[List[int]] = None


class ProposalResponse(BaseModel):
    id: int
    title: str
    customer_name: str
    customer_industry: Optional[str]
    requirements: str
    executive_summary: Optional[str]
    solution_overview: Optional[str]
    status: ProposalStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProposalDetail(ProposalResponse):
    technical_details: Optional[str]
    implementation_plan: Optional[str]
    pricing: Optional[dict]
    full_content: Optional[str]
    reference_documents: Optional[list]


class ProposalList(BaseModel):
    total: int
    items: List[ProposalResponse]


@router.post("/", response_model=ProposalResponse, status_code=status.HTTP_201_CREATED)
async def create_proposal(
    proposal_data: ProposalCreate, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)
):
    """创建新方案"""
    # XSS防护：清理用户输入
    sanitized_data = sanitize_for_api(
        {
            "title": proposal_data.title,
            "customer_name": proposal_data.customer_name,
            "customer_industry": proposal_data.customer_industry,
            "customer_contact": proposal_data.customer_contact,
            "requirements": proposal_data.requirements,
        }
    )

    # 创建方案记录
    db_proposal = Proposal(
        title=sanitized_data["title"],
        customer_name=sanitized_data["customer_name"],
        customer_industry=sanitized_data["customer_industry"],
        customer_contact=sanitized_data["customer_contact"],
        requirements=sanitized_data["requirements"],
        status=ProposalStatus.DRAFT,
        user_id=current_user.id,
    )

    if proposal_data.reference_document_ids:
        db_proposal.reference_documents = proposal_data.reference_document_ids

    db.add(db_proposal)
    db.commit()
    db.refresh(db_proposal)

    # ✅ 失效用户的方案列表缓存
    await cache_service.invalidate_user_proposals(current_user.id)
    logger.debug(f"📝 已失效用户 {current_user.id} 的方案列表缓存")

    return db_proposal


@router.post("/{proposal_id}/generate", response_model=ProposalDetail)
async def generate_proposal(
    proposal_id: int, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)
):
    """生成方案内容"""
    # 获取方案
    proposal = db.query(Proposal).filter(Proposal.id == proposal_id, Proposal.user_id == current_user.id).first()

    if not proposal:
        raise HTTPException(status_code=404, detail="方案不存在")

    # 更新状态为生成中
    proposal.status = ProposalStatus.GENERATING
    db.commit()

    try:
        # 使用AI生成方案
        generator = ProposalGenerator(db)
        result = await generator.generate(proposal)

        # 更新方案内容
        proposal.executive_summary = result.get("executive_summary")
        proposal.solution_overview = result.get("solution_overview")
        proposal.technical_details = result.get("technical_details")
        proposal.implementation_plan = result.get("implementation_plan")
        proposal.pricing = result.get("pricing")
        proposal.full_content = result.get("full_content")
        proposal.status = ProposalStatus.COMPLETED

        db.commit()
        db.refresh(proposal)

        # ✅ 失效用户的方案列表缓存（方案生成完成）
        await cache_service.invalidate_user_proposals(current_user.id)
        logger.debug(f"📝 已失效用户 {current_user.id} 的方案列表缓存")

        return proposal

    except Exception as e:
        # 记录详细错误信息
        logger.error(f"方案生成失败 - Proposal ID: {proposal_id}, User: {current_user.id}")
        logger.error(f"错误类型: {type(e).__name__}")
        logger.error(f"错误信息: {str(e)}")
        logger.exception("方案生成异常详情:")

        # 发生错误，恢复草稿状态
        proposal.status = ProposalStatus.DRAFT
        db.commit()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"方案生成失败: {type(e).__name__}: {str(e)}")


@router.get("/", response_model=ProposalList)
async def list_proposals(
    skip: int = 0,
    limit: int = 20,
    status_filter: Optional[ProposalStatus] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取方案列表 - 带缓存支持"""

    # ✅ 尝试从缓存获取
    filters = {"skip": skip, "limit": limit, "status": status_filter.value if status_filter else None}

    cached_result = await cache_service.get_proposal_list(user_id=current_user.id, filters=filters)

    if cached_result is not None:
        logger.info(f"✅ 方案列表缓存命中，返回 {len(cached_result.get('items', []))} 条记录")
        return cached_result

    # 缓存未命中，查询数据库
    query = db.query(Proposal).filter(Proposal.user_id == current_user.id)

    if status_filter:
        query = query.filter(Proposal.status == status_filter)

    total = query.count()
    items = query.order_by(Proposal.created_at.desc()).offset(skip).limit(limit).all()

    result = {"total": total, "items": items}

    # ✅ 缓存查询结果（5分钟）
    await cache_service.cache_proposal_list(user_id=current_user.id, filters=filters, proposals=result, expire=300)
    logger.debug(f"📝 方案列表已缓存，用户 {current_user.id}")

    return result


@router.get("/{proposal_id}", response_model=ProposalDetail)
async def get_proposal(
    proposal_id: int, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)
):
    """获取方案详情"""
    proposal = db.query(Proposal).filter(Proposal.id == proposal_id, Proposal.user_id == current_user.id).first()

    if not proposal:
        raise HTTPException(status_code=404, detail="方案不存在")

    return proposal


@router.put("/{proposal_id}", response_model=ProposalDetail)
async def update_proposal(
    proposal_id: int,
    proposal_data: ProposalCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """更新方案"""
    proposal = db.query(Proposal).filter(Proposal.id == proposal_id, Proposal.user_id == current_user.id).first()

    if not proposal:
        raise HTTPException(status_code=404, detail="方案不存在")

    # 更新字段
    proposal.title = proposal_data.title
    proposal.customer_name = proposal_data.customer_name
    proposal.customer_industry = proposal_data.customer_industry
    proposal.customer_contact = proposal_data.customer_contact
    proposal.requirements = proposal_data.requirements

    if proposal_data.reference_document_ids:
        proposal.reference_documents = proposal_data.reference_document_ids

    db.commit()
    db.refresh(proposal)

    # ✅ 失效用户的方案列表缓存（方案更新）
    await cache_service.invalidate_user_proposals(current_user.id)
    logger.debug(f"📝 已失效用户 {current_user.id} 的方案列表缓存")

    return proposal


@router.delete("/{proposal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_proposal(
    proposal_id: int, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)
):
    """删除方案"""
    proposal = db.query(Proposal).filter(Proposal.id == proposal_id, Proposal.user_id == current_user.id).first()

    if not proposal:
        raise HTTPException(status_code=404, detail="方案不存在")

    db.delete(proposal)
    db.commit()

    # ✅ 失效用户的方案列表缓存（方案删除）
    await cache_service.invalidate_user_proposals(current_user.id)
    logger.debug(f"📝 已失效用户 {current_user.id} 的方案列表缓存")

    return None


@router.get("/{proposal_id}/export")
async def export_proposal(
    proposal_id: int,
    format: str = "docx",  # docx, pdf, xlsx
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """导出方案"""
    proposal = db.query(Proposal).filter(Proposal.id == proposal_id, Proposal.user_id == current_user.id).first()

    if not proposal:
        raise HTTPException(status_code=404, detail="方案不存在")

    if proposal.status != ProposalStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="方案尚未生成完成")

    try:
        if format == "docx":
            filepath = export_service.export_proposal_to_word(proposal)
            return FileResponse(
                filepath,
                media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                filename=f"{proposal.title}.docx",
            )
        elif format == "pdf":
            filepath = export_service.export_proposal_to_pdf(proposal)
            return FileResponse(filepath, media_type="application/pdf", filename=f"{proposal.title}.pdf")
        elif format == "xlsx":
            filepath = export_service.export_pricing_to_excel(proposal)
            return FileResponse(
                filepath,
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                filename=f"{proposal.title}_报价单.xlsx",
            )
        else:
            raise HTTPException(status_code=400, detail=f"不支持的导出格式: {format}")

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"导出失败: {str(e)}")
