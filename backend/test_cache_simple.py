#!/usr/bin/env python3
"""
简化的缓存测试脚本

仅测试缓存服务本身的功能，不依赖其他服务
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from app.services.cache_service import cache_service
import time


async def test_basic_cache():
    """测试基础缓存操作"""
    print("\n" + "=" * 60)
    print("测试1: 基础缓存操作")
    print("=" * 60)
    
    try:
        # 设置缓存
        print("\n【步骤1】设置缓存")
        await cache_service.set("test_key", "test_value", ttl=60)
        print("  - ✅ 缓存设置成功")
        
        # 获取缓存
        print("\n【步骤2】获取缓存")
        value = await cache_service.get("test_key")
        print(f"  - 获取到的值: {value}")
        
        if value == "test_value":
            print("  - ✅ 缓存值正确")
        else:
            print(f"  - ❌ 缓存值错误: 期待 'test_value', 实际 '{value}'")
            return False
        
        # 检查存在
        print("\n【步骤3】检查键存在")
        exists = await cache_service.exists("test_key")
        print(f"  - 键存在: {exists}")
        
        if not exists:
            print("  - ❌ 键不存在（应该存在）")
            return False
        
        # 删除缓存
        print("\n【步骤4】删除缓存")
        await cache_service.delete("test_key")
        exists_after = await cache_service.exists("test_key")
        print(f"  - 删除后键存在: {exists_after}")
        
        if exists_after:
            print("  - ❌ 键仍然存在（应该已删除）")
            return False
        
        print("\n✅ 基础缓存操作测试通过")
        return True
        
    except Exception as e:
        print(f"\n❌ 基础缓存操作测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_ai_response_cache():
    """测试AI响应缓存"""
    print("\n" + "=" * 60)
    print("测试2: AI响应缓存")
    print("=" * 60)
    
    try:
        prompt = "介绍一下核心银行系统"
        response = "核心银行系统是银行的核心业务处理系统..."
        
        # 缓存AI响应
        print("\n【步骤1】缓存AI响应")
        success = await cache_service.cache_ai_response(prompt, response, expire=3600)
        print(f"  - 缓存成功: {success}")
        
        if not success:
            print("  - ❌ 缓存失败")
            return False
        
        # 获取缓存的AI响应
        print("\n【步骤2】获取缓存的AI响应")
        cached_response = await cache_service.get_ai_response(prompt)
        print(f"  - 缓存命中: {cached_response is not None}")
        
        if cached_response != response:
            print(f"  - ❌ 缓存值不匹配")
            return False
        
        print("\n✅ AI响应缓存测试通过")
        return True
        
    except Exception as e:
        print(f"\n❌ AI响应缓存测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_vector_search_cache():
    """测试向量搜索缓存"""
    print("\n" + "=" * 60)
    print("测试3: 向量搜索缓存")
    print("=" * 60)
    
    try:
        query = "核心银行系统"
        collection = "documents"
        results = [
            {"id": "doc_1", "content": "核心银行系统介绍..."},
            {"id": "doc_2", "content": "银行核心业务系统..."}
        ]
        
        # 缓存向量搜索结果
        print("\n【步骤1】缓存向量搜索结果")
        success = await cache_service.cache_vector_search(
            query=query,
            collection=collection,
            results=results,
            n_results=5,
            expire=1800
        )
        print(f"  - 缓存成功: {success}")
        
        if not success:
            print("  - ❌ 缓存失败")
            return False
        
        # 获取缓存的向量搜索结果
        print("\n【步骤2】获取缓存的向量搜索结果")
        cached_results = await cache_service.get_vector_search(
            query=query,
            collection=collection,
            n_results=5
        )
        print(f"  - 缓存命中: {cached_results is not None}")
        print(f"  - 结果数量: {len(cached_results) if cached_results else 0}")
        
        if cached_results != results:
            print(f"  - ❌ 缓存值不匹配")
            return False
        
        # 失效缓存
        print("\n【步骤3】失效向量搜索缓存")
        deleted = await cache_service.invalidate_vector_cache(collection)
        print(f"  - 已删除 {deleted} 个缓存键")
        
        # 验证失效
        cached_after = await cache_service.get_vector_search(
            query=query,
            collection=collection,
            n_results=5
        )
        
        if cached_after is not None:
            print(f"  - ❌ 缓存仍然存在（应该已失效）")
            return False
        
        print("\n✅ 向量搜索缓存测试通过")
        return True
        
    except Exception as e:
        print(f"\n❌ 向量搜索缓存测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_proposal_list_cache():
    """测试方案列表缓存"""
    print("\n" + "=" * 60)
    print("测试4: 方案列表缓存")
    print("=" * 60)
    
    try:
        user_id = 1
        filters = {"skip": 0, "limit": 20, "status": "completed"}
        proposals = {
            "total": 5,
            "items": [
                {"id": i, "title": f"方案{i}", "status": "completed"}
                for i in range(1, 6)
            ]
        }
        
        # 缓存方案列表
        print("\n【步骤1】缓存方案列表")
        success = await cache_service.cache_proposal_list(
            user_id=user_id,
            filters=filters,
            proposals=proposals,
            expire=300
        )
        print(f"  - 缓存成功: {success}")
        
        if not success:
            print("  - ❌ 缓存失败")
            return False
        
        # 获取缓存的方案列表
        print("\n【步骤2】获取缓存的方案列表")
        cached_proposals = await cache_service.get_proposal_list(
            user_id=user_id,
            filters=filters
        )
        print(f"  - 缓存命中: {cached_proposals is not None}")
        print(f"  - 方案数量: {len(cached_proposals.get('items', [])) if cached_proposals else 0}")
        
        if not cached_proposals:
            print(f"  - ❌ 缓存未命中")
            return False
        
        # 失效缓存
        print("\n【步骤3】失效用户方案列表缓存")
        deleted = await cache_service.invalidate_user_proposals(user_id)
        print(f"  - 已删除 {deleted} 个缓存键")
        
        # 验证失效
        cached_after = await cache_service.get_proposal_list(
            user_id=user_id,
            filters=filters
        )
        
        if cached_after is not None:
            print(f"  - ❌ 缓存仍然存在（应该已失效）")
            return False
        
        print("\n✅ 方案列表缓存测试通过")
        return True
        
    except Exception as e:
        print(f"\n❌ 方案列表缓存测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_cache_stats():
    """测试缓存统计"""
    print("\n" + "=" * 60)
    print("测试5: 缓存统计信息")
    print("=" * 60)
    
    try:
        stats = await cache_service.get_stats()
        
        print(f"\n【缓存统计】")
        print(f"  - 缓存类型: {stats['type']}")
        print(f"  - 缓存状态: {stats['status']}")
        print(f"  - 缓存键数: {stats['keys']}")
        print(f"  - 内存使用: {stats['memory_used']}")
        print(f"  - 命中率: {stats['hit_rate']}")
        print(f"  - 总请求数: {stats.get('total_requests', 'N/A')}")
        print(f"  - 命中次数: {stats.get('hits', 'N/A')}")
        print(f"  - 未命中次数: {stats.get('misses', 'N/A')}")
        
        if stats['type'] == 'redis' and stats['status'] == 'enabled':
            print("\n✅ Redis缓存运行正常")
            return True
        elif stats['type'] == 'memory':
            print("\n⚠️ 使用内存缓存（Redis不可用）")
            return True
        else:
            print(f"\n❌ 缓存状态异常: {stats['status']}")
            return False
        
    except Exception as e:
        print(f"\n❌ 缓存统计测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("缓存服务测试")
    print("=" * 60)
    print(f"测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    test_results = []
    
    # 运行所有测试
    test_results.append(("基础缓存操作", await test_basic_cache()))
    test_results.append(("AI响应缓存", await test_ai_response_cache()))
    test_results.append(("向量搜索缓存", await test_vector_search_cache()))
    test_results.append(("方案列表缓存", await test_proposal_list_cache()))
    test_results.append(("缓存统计信息", await test_cache_stats()))
    
    # 输出测试结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for test_name, result in test_results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name:20s} {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\n总计: {len(test_results)} 个测试")
    print(f"通过: {passed}")
    print(f"失败: {failed}")
    
    if failed == 0:
        print("\n🎉 所有测试通过！缓存服务运行正常")
        return 0
    else:
        print(f"\n⚠️ {failed} 个测试失败，请检查日志")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
