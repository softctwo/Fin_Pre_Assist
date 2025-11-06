"""向量服务测试"""
import pytest
from app.services.vector_service import VectorService


class TestVectorService:
    """测试向量服务"""

    @pytest.fixture
    def vector_service(self):
        """创建向量服务实例"""
        return VectorService()

    def test_add_document(self, vector_service):
        """测试添加文档"""
        vector_id = vector_service.add_document(
            doc_id=1,
            title="测试文档",
            content="这是一个测试文档，用于验证向量化功能。" * 50,
            metadata={"type": "test"}
        )
        assert vector_id is not None
        assert vector_id.startswith("doc_1_")

    def test_add_knowledge(self, vector_service):
        """测试添加知识库"""
        vector_id = vector_service.add_knowledge(
            knowledge_id=1,
            title="测试知识",
            content="测试知识内容",
            category="测试分类",
            metadata={"tag": "test"}
        )
        assert vector_id is not None
        assert vector_id.startswith("kb_1_")

    def test_search_documents(self, vector_service):
        """测试文档搜索"""
        # 先添加测试文档
        vector_service.add_document(
            doc_id=2,
            title="银行核心系统",
            content="银行核心系统是金融机构的核心业务处理系统，包括存款、贷款、账户管理等功能。",
            metadata={"type": "technical_proposal", "industry": "金融"}
        )

        # 搜索
        results = vector_service.search_documents(
            query="银行系统功能",
            n_results=5
        )
        assert len(results) > 0

    def test_search_knowledge(self, vector_service):
        """测试知识库搜索"""
        # 先添加测试知识
        vector_service.add_knowledge(
            knowledge_id=2,
            title="数字化转型",
            content="数字化转型是指企业利用数字技术改造业务流程、提升客户体验。",
            category="解决方案"
        )

        # 搜索
        results = vector_service.search_knowledge(
            query="企业数字化",
            n_results=5
        )
        assert len(results) > 0

    def test_text_splitting(self, vector_service):
        """测试文本分割"""
        long_text = "这是一段很长的文本。" * 200
        chunks = vector_service._split_text(long_text, max_length=500)
        assert len(chunks) > 1
        for chunk in chunks:
            assert len(chunk) <= 600  # 允许一些超出

    def test_delete_document(self, vector_service):
        """测试删除文档"""
        # 添加后删除
        vector_id = vector_service.add_document(
            doc_id=999,
            title="待删除文档",
            content="这个文档将被删除",
            metadata={}
        )
        result = vector_service.delete_document(vector_id)
        assert result is True

    def test_collection_stats(self, vector_service):
        """测试获取统计信息"""
        stats = vector_service.get_collection_stats()
        assert "documents" in stats
        assert "knowledge" in stats
        assert "proposals" in stats
        assert isinstance(stats["documents"], int)
