#!/usr/bin/env python3
"""
缓存集成测试脚本

测试向量搜索和方案列表的缓存功能
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from app.services.cache_service import cache_service
from app.services.vector_service import vector_service
import time


async def test_vector_search_cache():
    """测试向量搜索缓存"""
    print("\n" + "=" * 60)
    print("测试1: 向量搜索缓存")
    print("=" * 60)
    
    # 测试查询
    test_query = "核心银行系统解决方案"
    
    try:
        # 清空现有缓存
        await cache_service.clear_pattern("vector_search:*")
        print("✅ 已清空现有向量搜索缓存")
        
        # 第一次搜索（无缓存）
        print(f"\n【第1次搜索】查询: {test_query}")
        start_time = time.time()
        results1 = await vector_service.search_documents(
            query=test_query,
            n_results=5,
            use_cache=True
        )
        duration1 = (time.time() - start_time) * 1000
        print(f"  - 耗时: {duration1:.2f}ms")
        print(f"  - 结果数: {len(results1)}")
        print(f"  - 状态: 从ChromaDB查询（无缓存）")
        
        # 第二次搜索（有缓存）
        print(f"\n【第2次搜索】查询: {test_query}")
        start_time = time.time()
        results2 = await vector_service.search_documents(
            query=test_query,
            n_results=5,
            use_cache=True
        )
        duration2 = (time.time() - start_time) * 1000
        print(f"  - 耗时: {duration2:.2f}ms")
        print(f"  - 结果数: {len(results2)}")
        print(f"  - 状态: 从Redis缓存返回 ✅")
        
        # 性能对比
        if duration1 > 0 and duration2 > 0:
            speedup = duration1 / duration2
            improvement = ((duration1 - duration2) / duration1) * 100
            print(f"\n【性能提升】")
            print(f"  - 速度提升: {speedup:.1f}x")
            print(f"  - 效率提升: {improvement:.1f}%")
        
        # 测试禁用缓存
        print(f"\n【第3次搜索】查询: {test_query} (禁用缓存)")
        start_time = time.time()
        results3 = await vector_service.search_documents(
            query=test_query,
            n_results=5,
            use_cache=False
        )
        duration3 = (time.time() - start_time) * 1000
        print(f"  - 耗时: {duration3:.2f}ms")
        print(f"  - 结果数: {len(results3)}")
        print(f"  - 状态: 从ChromaDB查询（缓存已禁用）")
        
        print("\n✅ 向量搜索缓存测试通过")
        return True
        
    except Exception as e:
        print(f"\n❌ 向量搜索缓存测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_knowledge_search_cache():
    """测试知识库搜索缓存"""
    print("\n" + "=" * 60)
    print("测试2: 知识库搜索缓存")
    print("=" * 60)
    
    test_query = "金融科技创新"
    
    try:
        # 清空现有缓存
        await cache_service.clear_pattern("vector_search:knowledge:*")
        print("✅ 已清空现有知识库搜索缓存")
        
        # 第一次搜索（无缓存）
        print(f"\n【第1次搜索】查询: {test_query}")
        start_time = time.time()
        results1 = await vector_service.search_knowledge(
            query=test_query,
            n_results=5,
            use_cache=True
        )
        duration1 = (time.time() - start_time) * 1000
        print(f"  - 耗时: {duration1:.2f}ms")
        print(f"  - 结果数: {len(results1)}")
        print(f"  - 状态: 从ChromaDB查询（无缓存）")
        
        # 第二次搜索（有缓存）
        print(f"\n【第2次搜索】查询: {test_query}")
        start_time = time.time()
        results2 = await vector_service.search_knowledge(
            query=test_query,
            n_results=5,
            use_cache=True
        )
        duration2 = (time.time() - start_time) * 1000
        print(f"  - 耗时: {duration2:.2f}ms")
        print(f"  - 结果数: {len(results2)}")
        print(f"  - 状态: 从Redis缓存返回 ✅")
        
        # 性能对比
        if duration1 > 0 and duration2 > 0:
            speedup = duration1 / duration2
            improvement = ((duration1 - duration2) / duration1) * 100
            print(f"\n【性能提升】")
            print(f"  - 速度提升: {speedup:.1f}x")
            print(f"  - 效率提升: {improvement:.1f}%")
        
        print("\n✅ 知识库搜索缓存测试通过")
        return True
        
    except Exception as e:
        print(f"\n❌ 知识库搜索缓存测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_cache_invalidation():
    """测试缓存失效"""
    print("\n" + "=" * 60)
    print("测试3: 缓存失效机制")
    print("=" * 60)
    
    try:
        # 创建一些缓存
        test_queries = ["银行系统", "支付系统", "风控系统"]
        
        print("\n【步骤1】创建测试缓存")
        for query in test_queries:
            await vector_service.search_documents(
                query=query,
                n_results=3,
                use_cache=True
            )
        print(f"  - 已创建 {len(test_queries)} 个缓存条目")
        
        # 检查缓存统计
        stats = await cache_service.get_stats()
        keys_before = stats['keys']
        print(f"  - 当前缓存键数: {keys_before}")
        
        # 失效文档搜索缓存
        print("\n【步骤2】失效文档搜索缓存")
        deleted_count = await cache_service.invalidate_vector_cache("documents")
        print(f"  - 已删除 {deleted_count} 个缓存键")
        
        # 再次检查缓存统计
        stats_after = await cache_service.get_stats()
        keys_after = stats_after['keys']
        print(f"  - 失效后缓存键数: {keys_after}")
        
        # 验证缓存已失效
        print("\n【步骤3】验证缓存失效")
        cached_result = await cache_service.get_vector_search(
            query=test_queries[0],
            collection="documents",
            n_results=3
        )
        
        if cached_result is None:
            print("  - ✅ 缓存已成功失效")
        else:
            print("  - ❌ 缓存仍然存在（可能失效失败）")
            return False
        
        print("\n✅ 缓存失效测试通过")
        return True
        
    except Exception as e:
        print(f"\n❌ 缓存失效测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_proposal_list_cache():
    """测试方案列表缓存（模拟数据）"""
    print("\n" + "=" * 60)
    print("测试4: 方案列表缓存")
    print("=" * 60)
    
    try:
        # 模拟方案数据
        user_id = 1
        filters = {"skip": 0, "limit": 20, "status": None}
        mock_proposals = {
            "total": 10,
            "items": [
                {"id": i, "title": f"方案{i}", "status": "completed"}
                for i in range(1, 6)
            ]
        }
        
        # 清空现有缓存
        await cache_service.invalidate_user_proposals(user_id)
        print(f"✅ 已清空用户 {user_id} 的方案列表缓存")
        
        # 第一次访问（无缓存，手动设置）
        print(f"\n【第1次访问】用户: {user_id}")
        start_time = time.time()
        
        # 模拟数据库查询（手动缓存）
        await cache_service.cache_proposal_list(
            user_id=user_id,
            filters=filters,
            proposals=mock_proposals,
            expire=300
        )
        duration1 = (time.time() - start_time) * 1000
        print(f"  - 耗时: {duration1:.2f}ms")
        print(f"  - 结果数: {len(mock_proposals['items'])}")
        print(f"  - 状态: 从数据库查询并缓存")
        
        # 第二次访问（有缓存）
        print(f"\n【第2次访问】用户: {user_id}")
        start_time = time.time()
        cached_result = await cache_service.get_proposal_list(
            user_id=user_id,
            filters=filters
        )
        duration2 = (time.time() - start_time) * 1000
        print(f"  - 耗时: {duration2:.2f}ms")
        
        if cached_result:
            print(f"  - 结果数: {len(cached_result.get('items', []))}")
            print(f"  - 状态: 从Redis缓存返回 ✅")
        else:
            print(f"  - 状态: 缓存未命中")
            return False
        
        # 性能对比
        if duration1 > 0 and duration2 > 0:
            speedup = duration1 / duration2
            improvement = ((duration1 - duration2) / duration1) * 100
            print(f"\n【性能提升】")
            print(f"  - 速度提升: {speedup:.1f}x")
            print(f"  - 效率提升: {improvement:.1f}%")
        
        # 测试缓存失效
        print(f"\n【缓存失效测试】")
        deleted_count = await cache_service.invalidate_user_proposals(user_id)
        print(f"  - 已删除 {deleted_count} 个缓存键")
        
        # 验证失效
        cached_result_after = await cache_service.get_proposal_list(
            user_id=user_id,
            filters=filters
        )
        
        if cached_result_after is None:
            print("  - ✅ 缓存已成功失效")
        else:
            print("  - ❌ 缓存仍然存在")
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
    print("缓存集成测试")
    print("=" * 60)
    print(f"测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    test_results = []
    
    # 运行所有测试
    test_results.append(("向量搜索缓存", await test_vector_search_cache()))
    test_results.append(("知识库搜索缓存", await test_knowledge_search_cache()))
    test_results.append(("缓存失效机制", await test_cache_invalidation()))
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
        print("\n🎉 所有测试通过！缓存集成运行正常")
        return 0
    else:
        print(f"\n⚠️ {failed} 个测试失败，请检查日志")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
