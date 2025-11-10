"""多模型方案生成API"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime
from loguru import logger

from app.core.database import get_db
from app.models import Proposal, AIModel
from app.models.proposal import ProposalStatus
from app.api.auth import get_current_active_user
from app.services.proposal_generator import ProposalGenerator

router = APIRouter()


# Pydantic模型
class MultiModelProposalCreate(BaseModel):
    title: str
    customer_name: str
    customer_industry: Optional[str] = None
    customer_contact: Optional[str] = None
    requirements: str
    model_id: int  # 选择的模型ID
    reference_document_ids: Optional[List[int]] = None
    reference_template_id: Optional[int] = None


class ModelSelectionResponse(BaseModel):
    id: int
    name: str
    provider: str
    model_name: str
    is_enabled: bool
    description: Optional[str]
    success_rate: float

    model_config = ConfigDict(from_attributes=True)


class MultiModelProposalResponse(BaseModel):
    id: int
    title: str
    customer_name: str
    requirements: str
    executive_summary: Optional[str]
    solution_overview: Optional[str]
    technical_details: Optional[str]
    implementation_plan: Optional[str]
    pricing: Optional[dict]
    full_content: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


@router.get("/models/available", response_model=List[ModelSelectionResponse])
async def get_available_models(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """获取可用的AI模型列表（用于方案生成）"""
    models = db.query(AIModel).filter(
        AIModel.is_enabled == True
    ).all()
    
    return [
        ModelSelectionResponse(
            id=model.id,
            name=model.name,
            provider=model.provider,
            model_name=model.model_name,
            is_enabled=model.is_enabled,
            description=model.description,
            success_rate=model.success_rate
        )
        for model in models
    ]


@router.get("/models/default")
async def get_default_model(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """获取默认的AI模型"""
    default_model = db.query(AIModel).filter(
        AIModel.is_default == True,
        AIModel.is_enabled == True
    ).first()
    
    if not default_model:
        # 如果没有默认模型，返回第一个启用的模型
        default_model = db.query(AIModel).filter(
            AIModel.is_enabled == True
        ).first()
    
    if not default_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="没有可用的AI模型配置"
        )
    
    return ModelSelectionResponse.from_orm(default_model)


@router.post("/generate", response_model=MultiModelProposalResponse)
async def generate_proposal_with_model(
    proposal_data: MultiModelProposalCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """使用指定模型生成方案"""
    
    # 1. 获取模型配置
    model_config = db.query(AIModel).filter(
        AIModel.id == proposal_data.model_id,
        AIModel.is_enabled == True
    ).first()
    
    if not model_config:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="指定的AI模型不存在或未启用"
        )
    
    # 2. 创建方案记录
    proposal = Proposal(
        title=proposal_data.title,
        customer_name=proposal_data.customer_name,
        customer_industry=proposal_data.customer_industry,
        customer_contact=proposal_data.customer_contact,
        requirements=proposal_data.requirements,
        user_id=current_user.id,
        status=ProposalStatus.GENERATING
    )
    
    db.add(proposal)
    db.commit()
    db.refresh(proposal)
    
    try:
        # 3. 生成方案内容
        generator = ProposalGenerator(db, model_config)
        result = await generator.generate(proposal)
        
        # 4. 更新方案内容
        proposal.executive_summary = result.get("executive_summary")
        proposal.solution_overview = result.get("solution_overview")
        proposal.technical_details = result.get("technical_details")
        proposal.implementation_plan = result.get("implementation_plan")
        proposal.pricing = result.get("pricing")
        proposal.full_content = result.get("full_content")
        proposal.status = "completed"
        
        # 更新模型统计
        model_config.total_calls += 1
        model_config.success_calls += 1
        model_config.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(proposal)
        
        logger.info(f"使用模型 {model_config.name} 生成方案成功: {proposal.title}")
        
        return MultiModelProposalResponse.from_orm(proposal)
        
    except Exception as e:
        # 生成失败，更新状态
        proposal.status = "failed"
        proposal.full_content = f"生成失败: {str(e)}"
        
        # 更新模型统计
        model_config.total_calls += 1
        model_config.updated_at = datetime.utcnow()
        
        db.commit()
        
        logger.error(f"使用模型 {model_config.name} 生成方案失败: {str(e)}")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"方案生成失败: {str(e)}"
        )


@router.post("/preview")
async def preview_proposal_with_model(
    proposal_data: MultiModelProposalCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """预览方案生成效果（不保存到数据库）"""
    
    # 1. 获取模型配置
    model_config = db.query(AIModel).filter(
        AIModel.id == proposal_data.model_id,
        AIModel.is_enabled == True
    ).first()
    
    if not model_config:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="指定的AI模型不存在或未启用"
        )
    
    try:
        # 2. 创建临时方案对象用于生成
        temp_proposal = Proposal(
            title=proposal_data.title,
            customer_name=proposal_data.customer_name,
            customer_industry=proposal_data.customer_industry,
            customer_contact=proposal_data.customer_contact,
            requirements=proposal_data.requirements,
            created_by=current_user.id,
            status="generating"
        )
        
        # 3. 生成方案内容
        generator = ProposalGenerator(db, model_config)
        result = await generator.generate(temp_proposal)
        
        return {
            "preview": result,
            "model_info": {
                "id": model_config.id,
                "name": model_config.name,
                "provider": model_config.provider,
                "model_name": model_config.model_name
            }
        }
        
    except Exception as e:
        logger.error(f"预览方案失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"预览生成失败: {str(e)}"
        )


@router.get("/models/{model_id}/stats")
async def get_model_stats(
    model_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """获取模型使用统计"""
    
    model_config = db.query(AIModel).filter(
        AIModel.id == model_id
    ).first()
    
    if not model_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AI模型不存在"
        )
    
    return {
        "model": ModelSelectionResponse.from_orm(model_config),
        "total_calls": model_config.total_calls,
        "success_calls": model_config.success_calls,
        "total_tokens": model_config.total_tokens,
        "success_rate": model_config.success_rate,
        "created_at": model_config.created_at,
        "updated_at": model_config.updated_at
    }


@router.post("/compare")
async def compare_models(
    proposal_data: MultiModelProposalCreate,
    model_ids: List[int],
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """使用多个模型生成方案并对比"""
    
    if len(model_ids) > 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="最多同时对比3个模型"
        )
    
    # 获取模型配置
    models = db.query(AIModel).filter(
        AIModel.id.in_(model_ids),
        AIModel.is_enabled == True
    ).all()
    
    if len(models) != len(model_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="部分模型不存在或未启用"
        )
    
    results = []
    
    for model in models:
        try:
            # 创建临时方案对象
            temp_proposal = Proposal(
                title=f"[{model.name}] {proposal_data.title}",
                customer_name=proposal_data.customer_name,
                customer_industry=proposal_data.customer_industry,
                customer_contact=proposal_data.customer_contact,
                requirements=proposal_data.requirements,
                created_by=current_user.id,
                status="generating"
            )
            
            # 生成方案内容
            generator = ProposalGenerator(db, model)
            result = await generator.generate(temp_proposal)
            
            results.append({
                "model": ModelSelectionResponse.from_orm(model),
                "result": result,
                "success": True,
                "error": None
            })
            
        except Exception as e:
            results.append({
                "model": ModelSelectionResponse.from_orm(model),
                "result": None,
                "success": False,
                "error": str(e)
            })
            
            logger.error(f"模型 {model.name} 生成失败: {str(e)}")
    
    return {
        "proposal_data": proposal_data,
        "comparisons": results,
        "total_models": len(results),
        "successful_models": sum(1 for r in results if r["success"])
    }
