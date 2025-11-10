"""AI模型配置管理API"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from loguru import logger

from app.core.database import get_db
from app.models.ai_model import AIModel, PRESET_MODEL_CONFIGS
from app.api.auth import get_current_active_user
from app.services.ai_service import AIService
# from app.core.metrics import ai_models_total  # 暂时注释掉

router = APIRouter()


# Pydantic模型
class AIModelCreate(BaseModel):
    name: str
    provider: str
    model_name: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    max_tokens: int = 2000
    context_length: int = 4096
    temperature: float = 0.7
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    timeout: int = 120
    max_retries: int = 3
    headers: Optional[dict] = None
    extra_params: Optional[dict] = None
    description: Optional[str] = None
    is_enabled: bool = True


class AIModelUpdate(BaseModel):
    name: Optional[str] = None
    provider: Optional[str] = None
    model_name: Optional[str] = None
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    max_tokens: Optional[int] = None
    context_length: Optional[int] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    frequency_penalty: Optional[float] = None
    presence_penalty: Optional[float] = None
    timeout: Optional[int] = None
    max_retries: Optional[int] = None
    headers: Optional[dict] = None
    extra_params: Optional[dict] = None
    description: Optional[str] = None
    is_enabled: Optional[bool] = None


class AIModelResponse(BaseModel):
    id: int
    name: str
    provider: str
    model_name: str
    max_tokens: int
    context_length: int
    temperature: float
    top_p: float
    frequency_penalty: float
    presence_penalty: float
    timeout: int
    max_retries: int
    headers: Optional[dict]
    extra_params: Optional[dict]
    is_enabled: bool
    is_default: bool
    description: Optional[str]
    total_calls: int
    success_calls: int
    total_tokens: int
    success_rate: float
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ModelTestRequest(BaseModel):
    prompt: str = "请简单介绍一下你自己。"
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None


class ModelTestResponse(BaseModel):
    success: bool
    response: Optional[str] = None
    error: Optional[str] = None
    duration_ms: int
    tokens_used: Optional[int] = None


@router.get("/models", response_model=List[AIModelResponse])
async def get_ai_models(
    skip: int = 0,
    limit: int = 100,
    provider: Optional[str] = None,
    is_enabled: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """获取AI模型配置列表"""
    query = db.query(AIModel)
    
    if provider:
        query = query.filter(AIModel.provider == provider)
    if is_enabled is not None:
        query = query.filter(AIModel.is_enabled == is_enabled)
    
    models = query.offset(skip).limit(limit).all()
    return models


@router.get("/models/enabled", response_model=List[AIModelResponse])
async def get_enabled_ai_models(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """获取启用的AI模型列表"""
    models = db.query(AIModel).filter(AIModel.is_enabled == True).all()
    return models


@router.get("/models/{model_id}", response_model=AIModelResponse)
async def get_ai_model(
    model_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """获取单个AI模型配置"""
    model = db.query(AIModel).filter(AIModel.id == model_id).first()
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AI模型配置不存在"
        )
    return model


@router.post("/models", response_model=AIModelResponse)
async def create_ai_model(
    model_data: AIModelCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """创建AI模型配置"""
    
    # 检查模型名称是否重复
    existing = db.query(AIModel).filter(AIModel.name == model_data.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="模型名称已存在"
        )
    
    # 如果设置为默认模型，先取消其他默认模型
    if model_data.is_default:
        db.query(AIModel).filter(AIModel.is_default == True).update(
            {"is_default": False}
        )
    
    db_model = AIModel(**model_data.model_dump())
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    
    # ai_models_total.labels(provider=model_data.provider).inc()  # 暂时注释掉
    logger.info(f"创建AI模型配置: {model_data.name}")
    
    return db_model


@router.put("/models/{model_id}", response_model=AIModelResponse)
async def update_ai_model(
    model_id: int,
    model_data: AIModelUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """更新AI模型配置"""
    
    db_model = db.query(AIModel).filter(AIModel.id == model_id).first()
    if not db_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AI模型配置不存在"
        )
    
    # 检查模型名称是否重复
    if model_data.name and model_data.name != db_model.name:
        existing = db.query(AIModel).filter(
            AIModel.name == model_data.name,
            AIModel.id != model_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="模型名称已存在"
            )
    
    # 更新字段
    update_data = model_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_model, field, value)
    
    db_model.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_model)
    
    logger.info(f"更新AI模型配置: {model_id}")
    return db_model


@router.delete("/models/{model_id}")
async def delete_ai_model(
    model_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """删除AI模型配置"""
    
    db_model = db.query(AIModel).filter(AIModel.id == model_id).first()
    if not db_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AI模型配置不存在"
        )
    
    db.delete(db_model)
    db.commit()
    
    logger.info(f"删除AI模型配置: {model_id}")
    return {"message": "模型配置已删除"}


@router.post("/models/{model_id}/test", response_model=ModelTestResponse)
async def test_ai_model(
    model_id: int,
    test_request: ModelTestRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """测试AI模型连接"""
    
    db_model = db.query(AIModel).filter(AIModel.id == model_id).first()
    if not db_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AI模型配置不存在"
        )
    
    start_time = datetime.now()
    
    try:
        # 创建临时AI服务实例
        ai_service = AIService()
        ai_service._load_model_config(db_model)
        
        # 测试生成
        response = await ai_service.generate_text(
            prompt=test_request.prompt,
            temperature=test_request.temperature or db_model.temperature,
            max_tokens=test_request.max_tokens or db_model.max_tokens
        )
        
        duration = (datetime.now() - start_time).total_seconds() * 1000
        
        # 更新统计信息
        db_model.total_calls += 1
        db_model.success_calls += 1
        db.commit()
        
        return ModelTestResponse(
            success=True,
            response=response,
            duration_ms=int(duration)
        )
        
    except Exception as e:
        duration = (datetime.now() - start_time).total_seconds() * 1000
        
        # 更新统计信息
        db_model.total_calls += 1
        db.commit()
        
        logger.error(f"测试AI模型失败: {model_id}, 错误: {str(e)}")
        
        return ModelTestResponse(
            success=False,
            error=str(e),
            duration_ms=int(duration)
        )


@router.post("/models/{model_id}/set-default")
async def set_default_model(
    model_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """设置默认AI模型"""
    
    db_model = db.query(AIModel).filter(AIModel.id == model_id).first()
    if not db_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AI模型配置不存在"
        )
    
    # 取消所有其他模型的默认设置
    db.query(AIModel).update({"is_default": False})
    
    # 设置新的默认模型
    db_model.is_default = True
    db.commit()
    
    logger.info(f"设置默认AI模型: {model_id}")
    return {"message": "已设置为默认模型"}


@router.get("/models/presets")
async def get_preset_models(
    current_user = Depends(get_current_active_user)
):
    """获取预设模型配置"""
    return PRESET_MODEL_CONFIGS


@router.post("/models/presets/{preset_name}")
async def import_preset_model(
    preset_name: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """导入预设模型配置"""
    
    # 查找预设配置
    preset_config = None
    for preset in PRESET_MODEL_CONFIGS:
        if preset["name"] == preset_name:
            preset_config = preset
            break
    
    if not preset_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="预设模型不存在"
        )
    
    # 检查是否已存在
    existing = db.query(AIModel).filter(AIModel.name == preset_config["name"]).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该预设模型已存在"
        )
    
    # 创建新模型
    db_model = AIModel(**preset_config)
    db_model.is_enabled = False  # 导入的预设默认不启用
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    
    logger.info(f"导入预设AI模型: {preset_name}")
    return db_model


@router.get("/models/providers")
async def get_supported_providers(
    current_user = Depends(get_current_active_user)
):
    """获取支持的模型供应商列表"""
    return {
        "providers": [
            {
                "name": "openai",
                "display_name": "OpenAI",
                "description": "OpenAI官方模型，包括GPT系列"
            },
            {
                "name": "tongyi",
                "display_name": "通义千问",
                "description": "阿里云通义千问大模型"
            },
            {
                "name": "wenxin",
                "display_name": "文心一言",
                "description": "百度文心一言大模型"
            },
            {
                "name": "zhipu",
                "display_name": "智谱AI",
                "description": "智谱AI的GLM系列模型"
            },
            {
                "name": "deepseek",
                "display_name": "DeepSeek",
                "description": "DeepSeek开源大模型"
            }
        ]
    }
