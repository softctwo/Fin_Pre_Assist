"""
缓存失效测试
测试缓存的自动和手动失效机制
"""
import pytest
import sys
import os
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.services.cache_service import cache_service


@pytest.mark.asyncio
async def test_cache_invalidation_on_proposal_creation():
    """测试创建方案后缓存失效"""
    user_id = "test_user_123"

    # 先缓存一些数据
    await cache_service.cache_proposal_list(
        user_id=user_id,
        proposals=[{"id": 1, "title": "Test Proposal"}]
    )

    # 验证缓存存在
    cached = await cache_service.get_proposal_list(user_id, skip=0, limit=10)
    assert cached is not None

    # 失效用户方案缓存
    await cache_service.invalidate_user_proposals(user_id)

    # 验证缓存已失效
    cached_after = await cache_service.get_proposal_list(user_id, skip=0, limit=10)
    assert cached_after is None


@pytest.mark.asyncio
async def test_vector_cache_invalidation_on_document_upload():
    """测试文档上传后向量搜索缓存失效"""
    collection = "documents"

    # 缓存向量搜索结果
    await cache_service.cache_vector_search(
        collection=collection,
        query="金融系统",
        results=[{"id": "doc1", "score": 0.95}]
    )

    # 验证缓存存在
    cached = await cache_service.get_vector_search(collection, "金融系统")
    assert cached is not None

    # 失效向量缓存
    await cache_service.invalidate_vector_cache(collection)

    # 验证缓存已失效
    cached_after = await cache_service.get_vector_search(collection, "金融系统")
    assert cached_after is None


@pytest.mark.asyncio
async def test_pattern_based_cache_invalidation():
    """测试基于模式的缓存批量失效"""
    # 创建多个缓存键
    await cache_service.redis.set("user:1:proposals", "data1")
    await cache_service.redis.set("user:2:proposals", "data2")
    await cache_service.redis.set("user:3:documents", "data3")

    # 批量失效所有用户方案缓存
    await cache_service.clear_pattern("user:*:proposals")

    # 验证匹配模式已删除
    assert await cache_service.redis.get("user:1:proposals") is None
    assert await cache_service.redis.get("user:2:proposals") is None

    # 验证不匹配的模式保留
    assert await cache_service.redis.get("user:3:documents") is not None


@pytest.mark.asyncio
async def test_cache_ttl_expiration():
    """测试缓存TTL过期"""
    key = "test_ttl_key"
    value = "test_value"

    # 设置1秒过期
    await cache_service.redis.setex(key, 1, value)

    # 立即验证存在
    assert await cache_service.redis.get(key) == value

    # 等待过期
    await asyncio.sleep(1.5)

    # 验证已过期
    assert await cache_service.redis.get(key) is None


@pytest.mark.asyncio
async def test_cache_stats_after_invalidation():
    """测试缓存失效后的统计信息"""
    # 添加一些缓存
    await cache_service.cache_ai_response("query1", "result1")
    await cache_service.cache_ai_response("query2", "result2")

    # 获取初始统计
    stats_before = await cache_service.get_stats()

    # 失效一个缓存
    await cache_service.redis.delete("ai:response:" + cache_service._hash_key("query1"))

    # 获取更新后统计
    stats_after = await cache_service.get_stats()

    assert stats_after['keys_count'] == stats_before['keys_count'] - 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
