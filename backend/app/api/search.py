"""语义搜索API"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional

from app.core.database import get_db
from app.models import User
from app.api.auth import get_current_active_user
from app.services.vector_service import vector_service

router = APIRouter()


class SearchResult(BaseModel):
    """搜索结果"""

    id: str
    content: str
    metadata: dict
    relevance_score: float


class SearchResponse(BaseModel):
    """搜索响应"""

    query: str
    total: int
    results: List[SearchResult]


@router.post("/documents", response_model=SearchResponse)
async def search_documents(
    query: str = Query(..., description="搜索查询"),
    limit: int = Query(5, ge=1, le=20, description="返回结果数量"),
    doc_type: Optional[str] = Query(None, description="文档类型过滤"),
    industry: Optional[str] = Query(None, description="行业过滤"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """语义搜索文档"""
    # 构建过滤条件
    filter_metadata = {}
    if doc_type:
        filter_metadata["type"] = doc_type
    if industry:
        filter_metadata["industry"] = industry

    # 执行搜索
    results = vector_service.search_documents(
        query=query, n_results=limit, filter_metadata=filter_metadata if filter_metadata else None
    )

    # 格式化结果
    formatted_results = []
    for result in results:
        formatted_results.append(
            SearchResult(
                id=result["id"],
                content=result["document"][:200] + "..." if len(result["document"]) > 200 else result["document"],
                metadata=result["metadata"],
                relevance_score=1.0 - result["distance"] if result["distance"] else 0.0,
            )
        )

    return SearchResponse(query=query, total=len(formatted_results), results=formatted_results)


@router.post("/knowledge", response_model=SearchResponse)
async def search_knowledge(
    query: str = Query(..., description="搜索查询"),
    limit: int = Query(5, ge=1, le=20, description="返回结果数量"),
    category: Optional[str] = Query(None, description="分类过滤"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """语义搜索知识库"""
    # 执行搜索
    results = vector_service.search_knowledge(query=query, n_results=limit, category=category)

    # 格式化结果
    formatted_results = []
    for result in results:
        formatted_results.append(
            SearchResult(
                id=result["id"],
                content=result["document"][:200] + "..." if len(result["document"]) > 200 else result["document"],
                metadata=result["metadata"],
                relevance_score=1.0 - result["distance"] if result["distance"] else 0.0,
            )
        )

    return SearchResponse(query=query, total=len(formatted_results), results=formatted_results)


@router.post("/proposals/similar")
async def search_similar_proposals(
    requirements: str = Query(..., description="需求描述"),
    limit: int = Query(3, ge=1, le=10, description="返回结果数量"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """搜索相似的历史方案"""
    results = vector_service.search_similar_proposals(requirements=requirements, n_results=limit)

    # 格式化结果
    formatted_results = []
    for result in results:
        formatted_results.append(
            SearchResult(
                id=result["id"],
                content=result["document"][:300] + "..." if len(result["document"]) > 300 else result["document"],
                metadata=result["metadata"],
                relevance_score=1.0 - result["distance"] if result["distance"] else 0.0,
            )
        )

    return SearchResponse(query=requirements, total=len(formatted_results), results=formatted_results)


@router.get("/stats")
async def get_search_stats(current_user: User = Depends(get_current_active_user)):
    """获取向量数据库统计信息"""
    stats = vector_service.get_collection_stats()
    return {"status": "ok", "collections": stats}
