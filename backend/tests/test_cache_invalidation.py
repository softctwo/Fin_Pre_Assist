"""缓存与向量搜索失效测试"""
import pytest

from app.services.cache_service import CacheService


@pytest.fixture
def memory_cache():
    """提供仅使用内存的缓存服务实例"""
    service = CacheService()
    service._cache_type = "memory"
    service._memory_cache.clear()
    service._hits = 0
    service._misses = 0
    return service


@pytest.mark.asyncio
async def test_proposal_cache_roundtrip(memory_cache):
    user_id = 42
    await memory_cache.cache_proposal_list(user_id, {"status": None}, {"items": [{"id": 1}]})

    cached = await memory_cache.get_proposal_list(user_id, {"status": None})
    assert cached is not None
    assert cached["items"][0]["id"] == 1

    await memory_cache.invalidate_user_proposals(user_id)
    cached_after = await memory_cache.get_proposal_list(user_id, {"status": None})
    assert cached_after is None


@pytest.mark.asyncio
async def test_vector_cache_invalidation(memory_cache):
    filters = {"type": "technical_proposal"}
    await memory_cache.cache_vector_search(
        query="核心系统",
        collection="documents",
        results=[{"id": "chunk1"}],
        filter_metadata=filters
    )

    cached = await memory_cache.get_vector_search(
        query="核心系统",
        collection="documents",
        filter_metadata=filters
    )
    assert cached is not None

    await memory_cache.invalidate_vector_cache("documents")
    cached_after = await memory_cache.get_vector_search(
        query="核心系统",
        collection="documents",
        filter_metadata=filters
    )
    assert cached_after is None


@pytest.mark.asyncio
async def test_clear_pattern_on_memory_cache(memory_cache):
    memory_cache._memory_cache["proposal_list:demo"] = {"items": []}
    memory_cache._memory_cache["vector_search:documents:q"] = []

    cleared = await memory_cache.clear_pattern("proposal_list*")
    assert cleared == 1
    assert "proposal_list:demo" not in memory_cache._memory_cache
    assert "vector_search:documents:q" in memory_cache._memory_cache


@pytest.mark.asyncio
async def test_cache_stats(memory_cache):
    await memory_cache.cache_ai_response("prompt", "response")
    await memory_cache.get_ai_response("prompt")

    stats = await memory_cache.get_stats()
    assert stats["type"] == "memory"
    assert stats["hits"] >= 1
    assert "hit_rate" in stats
