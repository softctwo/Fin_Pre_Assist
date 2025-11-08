"""
向量服务 - 集成测试
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
import numpy as np
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.services.vector_service import vector_service
from app.services.cache_service import cache_service


class TestVectorIntegration:
    """向量服务集成测试"""


    @pytest.fixture
    def sample_documents(self):
        """示例文档"""
        return [
            {
                "id": "doc1",
                "content": "这是一篇关于银行核心系统的文档",
                "meta": {"type": "proposal", "industry": "银行"}
            },
            {
                "id": "doc2",
                "content": "金融科技解决方案，包括移动支付和区块链",
                "meta": {"type": "solution", "industry": "金融科技"}
            },
            {
                "id": "doc3",
                "content": "数据库优化和安全防护措施",
                "meta": {"type": "technical", "industry": "通用"}
            }
        ]


    @pytest.mark.asyncio
    async def test_add_and_search_documents(self, sample_documents):
        """测试添加文档并搜索"""
        with patch('httpx.AsyncClient.post') as mock_post:
            # 模拟向量化的响应
            mock_post.return_value = Mock()
            mock_post.return_value.json = Mock(return_value={
                "data": [{"embedding": [0.1] * 150}]
            })

            # 添加文档
            for doc in sample_documents:
                result = await vector_service.add_document(
                    id=doc["id"],
                    content=doc["content"],
                    metadata=doc["meta"]
                )
                assert result is not None


    @pytest.mark.asyncio
    async def test_search_with_filters(self, sample_documents):
        """测试带过滤条件的搜索"""
        # 添加文档到向量数据库
        for doc in sample_documents:
            vector_service.collection.add(
                ids=[doc["id"]],
                documents=[doc["content"]],
                metadatas=[doc["meta"]]
            )

        # 测试行业过滤
        results = await vector_service.search_documents(
            query="银行系统",
            n_results=2,
            filters={"industry": "银行"}
        )

        assert len(results) > 0


    @pytest.mark.asyncio
    async def test_semantic_similarity(self):
        """测试语义相似度搜索"""
        # 添加相似内容
        vector_service.collection.add(
            ids=["tech1", "tech2", "tech3"],
            documents=[
                "人工智能在金融科技中的应用",
                "AI技术改变银行业务模式",
                "传统银行系统的局限性"
            ],
            metadatas=[
                {"topic": "AI"},
                {"topic": "AI"},
                {"topic": "traditional"}
            ]
        )

        # 搜索AI相关内容
        results = await vector_service.search_documents(
            query="人工智能和机器学习",
            n_results=3
        )

        assert len(results) >= 2
        # AI相关的结果应该排名靠前
        ai_results = [r for r in results if "AI" in r.get("metadata", {}).get("topic", "")]
        assert len(ai_results) >= 2


    @pytest.mark.asyncio
    async def test_search_knowledge_by_category(self):
        """测试按分类搜索知识库"""
        # 添加知识库条目
        categories = ["产品介绍", "解决方案", "案例库", "技术文档"]

        for i, category in enumerate(categories):
            await vector_service.upsert_knowledge(
                id=f"kg{i}",
                content=f"这是{category}的详细内容",
                category=category,
                title=f"示例{category}"
            )

        # 搜索特定分类
        results = await vector_service.search_knowledge(
            query="产品功能",
            n_results=2,
            category="产品介绍"
        )

        for result in results:
            assert result.get("category") == "产品介绍"


    @pytest.mark.asyncio
    async def test_similar_proposals_search(self):
        """测试相似方案搜索"""
        # 创建多个方案
        proposals_data = [
            {
                "id": "p1",
                "requirements": "核心银行系统升级改造",
                "content": "实施核心银行系统升级，包括账户管理、支付结算等模块"
            },
            {
                "id": "p2",
                "requirements": "移动银行应用开发",
                "content": "开发移动端银行应用，支持转账、理财、贷款申请"
            },
            {
                "id": "p3",
                "requirements": "银行核心系统性能优化",
                "content": "优化核心系统性能，提升交易处理能力至10000TPS"
            }
        ]

        # 添加到向量数据库
        for proposal in proposals_data:
            await vector_service.vectorize_proposal(
                proposal_id=proposal["id"],
                requirements=proposal["requirements"],
                content=proposal["content"]
            )

        # 搜索相似方案
        similar = await vector_service.search_similar_proposals(
            query="银行系统升级和改造",
            n_results=3
        )

        assert len(similar) >= 2  # 应该找到至少2个相似方案
        # 核心系统相关的方案应该得分更高
        scores = [r.get("score", 0) for r in similar]
        assert all(score > 0.3 for score in scores)


    @pytest.mark.asyncio
    async def test_update_document_vector(self):
        """测试更新文档向量"""
        doc_id = "doc_to_update"

        # 添加初始文档
        vector_service.collection.add(
            ids=[doc_id],
            documents=["初始内容"],
            metadatas=[{"version": "1.0"}]
        )

        # 更新文档
        update_result = await vector_service.update_document(
            id=doc_id,
            new_content="更新后的内容，增加了更多详细信息",
            new_metadata={"version": "2.0", "updated": True}
        )

        assert update_result is True

        # 验证更新后的搜索结果
        results = await vector_service.search_documents(
            query="详细信息",
            n_results=1,
            filters={"id": doc_id}
        )

        assert len(results) > 0
        assert results[0].get("metadata", {}).get("version") == "2.0"


    @pytest.mark.asyncio
    async def test_delete_document_and_verify(self):
        """测试删除文档并验证"""
        doc_id = "doc_to_delete"

        # 添加文档
        vector_service.collection.add(
            ids=[doc_id],
            documents=["待删除的文档"],
            metadatas=[{"status": "pending_delete"}]
        )

        # 删除前验证存在
        before_delete = vector_service.collection.get(ids=[doc_id])
        assert len(before_delete["ids"]) == 1

        # 删除文档
        delete_result = await vector_service.delete_document(doc_id)
        assert delete_result is True

        # 验证已删除
        after_delete = vector_service.collection.get(ids=[doc_id])
        assert len(after_delete["ids"]) == 0


    @pytest.mark.asyncio
    async def test_cache_integration(self):
        """测试向量搜索与缓存的集成"""
        query = "银行系统测试"
        collection = "documents"

        # 第一次搜索（无缓存）
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_post.return_value = Mock()
            mock_post.return_value.json = Mock(return_value={
                "data": [{"embedding": [0.5] * 150}]
            })

            results1 = await vector_service.search_documents(
                query=query,
                n_results=5,
                use_cache=True
            )

            assert mock_post.call_count > 0

        # 第二次搜索（有缓存）
        results2 = await vector_service.search_documents(
            query=query,
            n_results=5,
            use_cache=True
        )

        # 验证两次结果相同
        assert len(results1) == len(results2)


    @pytest.mark.asyncio
    async def test_cache_invalidation(self):
        """测试缓存失效"""
        query = "金融科技"
        collection = "knowledge"

        # 搜索并缓存
        await vector_service.search_knowledge(
            query=query,
            n_results=5,
            use_cache=True
        )

        # 验证缓存存在
        cached = await cache_service.get_vector_search(collection, query)
        assert cached is not None

        # 添加新知识并失效缓存
        await vector_service.upsert_knowledge(
            id="new_knowledge",
            content="这是新的金融科技知识",
            category="技术"
        )

        # 验证缓存已失效
        cached_after = await cache_service.get_vector_search(collection, query)
        assert cached_after is None


    @pytest.mark.asyncio
    async def test_vector_distance_calculation(self):
        """测试向量距离计算"""
        # 添加相似度不同的文档
        documents = [
            "Python编程语言基础教程",
            "Java编程语言入门指南",
            "JavaScript前端开发框架",
            "数据库设计与优化",
            "网络协议和通信原理"
        ]

        for i, doc in enumerate(documents):
            vector_service.collection.add(
                ids=[f"tech{i}"],
                documents=[doc],
                metadatas=[{"id": f"tech{i}"}]
            )

        # 搜索编程相关内容
        results = await vector_service.search_documents(
            query="Python编程",
            n_results=5
        )

        # 验证相关性排序
        assert len(results) >= 3
        # Python文档应该排名最高
        python_result = next((r for r in results if "Python" in r.get("document", "")), None)
        if python_result:
            assert python_result.get("rank") == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
