from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.config import settings
from app.core.metrics import (
    ai_calls_total,
    ai_tokens_used,
    vector_search_total,
    counter_total,
)
from app.models import Document, Proposal
from app.services.cache_service import cache_service

router = APIRouter()


@router.get("/summary")
async def get_metrics_summary(
    db: Session = Depends(get_db),
):
    """返回仪表盘所需的监控摘要"""
    document_count = db.query(Document).count()
    proposal_count = db.query(Proposal).count()
    cache_stats = await cache_service.get_stats()

    summary = {
        "documents": document_count,
        "proposals": proposal_count,
        "cache_hit_rate": cache_stats.get("hit_rate"),
        "cache_type": cache_stats.get("type"),
        "cache_keys": cache_stats.get("keys"),
        "ai_provider": settings.AI_PROVIDER,
        "ai_calls": int(counter_total(ai_calls_total)),
        "ai_tokens": int(counter_total(ai_tokens_used)),
        "vector_searches": int(counter_total(vector_search_total)),
    }
    return summary
