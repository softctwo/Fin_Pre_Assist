from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.models import KnowledgeBase

router = APIRouter()

# Pydantic模型
class KnowledgeCreate(BaseModel):
    category: str
    title: str
    content: str
    tags: Optional[List[str]] = None
    metadata: Optional[dict] = None


class KnowledgeUpdate(BaseModel):
    category: Optional[str] = None
    title: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[List[str]] = None
    metadata: Optional[dict] = None


class KnowledgeResponse(BaseModel):
    id: int
    category: str
    title: str
    tags: Optional[list]
    weight: int
    is_active: int
    created_at: datetime

    class Config:
        from_attributes = True


class KnowledgeDetail(KnowledgeResponse):
    content: str
    metadata: Optional[dict]


class KnowledgeList(BaseModel):
    total: int
    items: List[KnowledgeResponse]


@router.post("/", response_model=KnowledgeResponse, status_code=status.HTTP_201_CREATED)
async def create_knowledge(
    knowledge_data: KnowledgeCreate,
    db: Session = Depends(get_db)
):
    """创建知识库条目"""
    db_knowledge = KnowledgeBase(
        category=knowledge_data.category,
        title=knowledge_data.title,
        content=knowledge_data.content,
        tags=knowledge_data.tags,
        metadata=knowledge_data.metadata
    )

    db.add(db_knowledge)
    db.commit()
    db.refresh(db_knowledge)

    return db_knowledge


@router.get("/", response_model=KnowledgeList)
async def list_knowledge(
    skip: int = 0,
    limit: int = 50,
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取知识库列表"""
    query = db.query(KnowledgeBase).filter(KnowledgeBase.is_active == 1)

    if category:
        query = query.filter(KnowledgeBase.category == category)

    total = query.count()
    items = query.order_by(KnowledgeBase.weight.desc(), KnowledgeBase.created_at.desc()).offset(skip).limit(limit).all()

    return {"total": total, "items": items}


@router.get("/categories")
async def list_categories(db: Session = Depends(get_db)):
    """获取所有分类"""
    categories = db.query(KnowledgeBase.category).filter(
        KnowledgeBase.is_active == 1
    ).distinct().all()

    return {"categories": [cat[0] for cat in categories]}


@router.get("/{knowledge_id}", response_model=KnowledgeDetail)
async def get_knowledge(
    knowledge_id: int,
    db: Session = Depends(get_db)
):
    """获取知识库详情"""
    knowledge = db.query(KnowledgeBase).filter(
        KnowledgeBase.id == knowledge_id,
        KnowledgeBase.is_active == 1
    ).first()

    if not knowledge:
        raise HTTPException(status_code=404, detail="知识库条目不存在")

    return knowledge


@router.put("/{knowledge_id}", response_model=KnowledgeDetail)
async def update_knowledge(
    knowledge_id: int,
    knowledge_data: KnowledgeUpdate,
    db: Session = Depends(get_db)
):
    """更新知识库条目"""
    knowledge = db.query(KnowledgeBase).filter(
        KnowledgeBase.id == knowledge_id
    ).first()

    if not knowledge:
        raise HTTPException(status_code=404, detail="知识库条目不存在")

    # 更新字段
    if knowledge_data.category:
        knowledge.category = knowledge_data.category
    if knowledge_data.title:
        knowledge.title = knowledge_data.title
    if knowledge_data.content:
        knowledge.content = knowledge_data.content
    if knowledge_data.tags is not None:
        knowledge.tags = knowledge_data.tags
    if knowledge_data.metadata is not None:
        knowledge.metadata = knowledge_data.metadata

    db.commit()
    db.refresh(knowledge)

    return knowledge


@router.delete("/{knowledge_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_knowledge(
    knowledge_id: int,
    db: Session = Depends(get_db)
):
    """删除知识库条目（软删除）"""
    knowledge = db.query(KnowledgeBase).filter(
        KnowledgeBase.id == knowledge_id
    ).first()

    if not knowledge:
        raise HTTPException(status_code=404, detail="知识库条目不存在")

    # 软删除
    knowledge.is_active = 0
    db.commit()

    return None


@router.post("/search")
async def search_knowledge(
    query: str,
    category: Optional[str] = None,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """搜索知识库"""
    # TODO: 实现语义搜索
    # 这里先实现简单的关键词搜索
    search_query = db.query(KnowledgeBase).filter(
        KnowledgeBase.is_active == 1
    )

    if category:
        search_query = search_query.filter(KnowledgeBase.category == category)

    # 简单的关键词匹配
    search_query = search_query.filter(
        (KnowledgeBase.title.contains(query)) |
        (KnowledgeBase.content.contains(query))
    )

    results = search_query.order_by(
        KnowledgeBase.weight.desc()
    ).limit(limit).all()

    return {"results": results, "total": len(results)}
