"""AI向量化功能单元测试"""
import os
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from app.services.ai_service import AIService

pytestmark = pytest.mark.skipif(
    os.getenv("ENABLE_AI_EMBED_TESTS") != "1",
    reason="AI embedding live tests disabled (set ENABLE_AI_EMBED_TESTS=1 to run)",
)


class TestAIEmbeddings:
    """AI文本向量化测试类"""
    
    @pytest.fixture
    def zhipu_service(self):
        """创建智谱AI服务实例"""
        with patch('app.services.ai_service.settings') as mock_settings:
            mock_settings.AI_PROVIDER = 'zhipu'
            mock_settings.ZHIPU_API_KEY = 'test_key'
            service = AIService()
            service.provider = 'zhipu'
            return service
    
    @pytest.fixture
    def tongyi_service(self):
        """创建通义千问服务实例"""
        with patch('app.services.ai_service.settings') as mock_settings:
            mock_settings.AI_PROVIDER = 'tongyi'
            mock_settings.TONGYI_API_KEY = 'test_key'
            service = AIService()
            service.provider = 'tongyi'
            return service
    
    @pytest.fixture
    def wenxin_service(self):
        """创建文心一言服务实例"""
        with patch('app.services.ai_service.settings') as mock_settings:
            mock_settings.AI_PROVIDER = 'wenxin'
            mock_settings.WENXIN_API_KEY = 'test_key'
            service = AIService()
            service.provider = 'wenxin'
            return service
    
    @pytest.fixture
    def openai_service(self):
        """创建OpenAI服务实例"""
        with patch('app.services.ai_service.settings') as mock_settings:
            mock_settings.AI_PROVIDER = 'openai'
            mock_settings.OPENAI_API_KEY = 'test_key'
            service = AIService()
            service.provider = 'openai'
            return service
    
    @pytest.mark.asyncio
    async def test_zhipu_embed_text(self, zhipu_service):
        """测试智谱AI文本向量化"""
        # Mock智谱AI client响应
        mock_response = Mock()
        mock_response.data = [Mock(embedding=[0.1, 0.2, 0.3, 0.4])]
        
        with patch.object(zhipu_service.client.embeddings, 'create', return_value=mock_response):
            result = await zhipu_service.embed_text("测试文本")
            
            assert isinstance(result, list)
            assert len(result) == 4
            assert result == [0.1, 0.2, 0.3, 0.4]
    
    @pytest.mark.asyncio
    async def test_tongyi_embed_text(self, tongyi_service):
        """测试通义千问文本向量化"""
        # Mock通义千问响应
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.output = {
            'embeddings': [
                {'embedding': [0.5, 0.6, 0.7, 0.8]}
            ]
        }
        
        with patch('app.services.ai_service.dashscope') as mock_dashscope:
            mock_dashscope.api_key = 'test_key'
            with patch('app.services.ai_service.TextEmbedding') as mock_text_embedding:
                mock_text_embedding.call.return_value = mock_response
                
                result = await tongyi_service.embed_text("测试文本")
                
                assert isinstance(result, list)
                assert len(result) == 4
                assert result == [0.5, 0.6, 0.7, 0.8]
    
    @pytest.mark.asyncio
    async def test_wenxin_embed_text(self, wenxin_service):
        """测试文心一言文本向量化"""
        # Mock文心一言响应
        mock_response = Mock()
        mock_response.get_result.return_value = [[0.9, 1.0, 1.1, 1.2]]
        
        with patch('app.services.ai_service.erniebot') as mock_erniebot:
            mock_erniebot.api_type = 'aistudio'
            mock_erniebot.access_token = 'test_key'
            mock_erniebot.Embedding.create.return_value = mock_response
            
            result = await wenxin_service.embed_text("测试文本")
            
            assert isinstance(result, list)
            assert len(result) == 4
            assert result[0] == [0.9, 1.0, 1.1, 1.2]
    
    @pytest.mark.asyncio
    async def test_openai_embed_text(self, openai_service):
        """测试OpenAI文本向量化"""
        # Mock OpenAI响应
        mock_response = Mock()
        mock_response.data = [Mock(embedding=[1.3, 1.4, 1.5, 1.6])]
        
        with patch('app.services.ai_service.AsyncOpenAI') as mock_openai:
            mock_client = AsyncMock()
            mock_client.embeddings.create = AsyncMock(return_value=mock_response)
            mock_openai.return_value = mock_client
            
            result = await openai_service.embed_text("测试文本")
            
            assert isinstance(result, list)
            assert len(result) == 4
            assert result == [1.3, 1.4, 1.5, 1.6]
    
    @pytest.mark.asyncio
    async def test_unsupported_provider_embed(self):
        """测试不支持的提供商"""
        service = AIService()
        service.provider = 'unsupported'
        
        with pytest.raises(NotImplementedError) as exc_info:
            await service.embed_text("测试文本")
        
        assert "unsupported" in str(exc_info.value)
        assert "未实现" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_embed_empty_text(self, zhipu_service):
        """测试空文本向量化"""
        mock_response = Mock()
        mock_response.data = [Mock(embedding=[])]
        
        with patch.object(zhipu_service.client.embeddings, 'create', return_value=mock_response):
            result = await zhipu_service.embed_text("")
            
            assert isinstance(result, list)
            assert len(result) == 0
    
    @pytest.mark.asyncio
    async def test_embed_long_text(self, zhipu_service):
        """测试长文本向量化"""
        long_text = "测试" * 1000  # 2000个字符
        mock_response = Mock()
        mock_response.data = [Mock(embedding=[0.1] * 1536)]  # 智谱AI embedding维度
        
        with patch.object(zhipu_service.client.embeddings, 'create', return_value=mock_response):
            result = await zhipu_service.embed_text(long_text)
            
            assert isinstance(result, list)
            assert len(result) == 1536
    
    @pytest.mark.asyncio
    async def test_zhipu_api_error(self, zhipu_service):
        """测试智谱AI API错误"""
        with patch.object(zhipu_service.client.embeddings, 'create', side_effect=Exception("API Error")):
            with pytest.raises(Exception) as exc_info:
                await zhipu_service.embed_text("测试文本")
            
            assert "文本向量化失败" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_tongyi_api_error(self, tongyi_service):
        """测试通义千问API错误"""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.message = "Invalid request"
        
        with patch('app.services.ai_service.dashscope'):
            with patch('app.services.ai_service.TextEmbedding') as mock_text_embedding:
                mock_text_embedding.call.return_value = mock_response
                
                with pytest.raises(Exception) as exc_info:
                    await tongyi_service.embed_text("测试文本")
                
                assert "通义千问Embedding API返回错误" in str(exc_info.value)


class TestSemanticSearch:
    """语义搜索测试类"""
    
    @pytest.fixture
    def service(self):
        """创建AI服务实例"""
        with patch('app.services.ai_service.settings') as mock_settings:
            mock_settings.AI_PROVIDER = 'zhipu'
            mock_settings.ZHIPU_API_KEY = 'test_key'
            return AIService()
    
    @pytest.mark.asyncio
    async def test_semantic_search_basic(self, service):
        """测试基本语义搜索"""
        query = "人工智能技术"
        documents = [
            "人工智能是计算机科学的一个分支",
            "机器学习是人工智能的子领域",
            "今天天气很好"
        ]
        
        # Mock embed_text方法
        async def mock_embed_text(text):
            # 简化的向量表示
            if "人工智能" in text or "机器学习" in text:
                return [1.0, 0.8, 0.2]
            else:
                return [0.1, 0.1, 0.9]
        
        with patch.object(service, 'embed_text', side_effect=mock_embed_text):
            results = await service.semantic_search(query, documents, top_k=2)
            
            assert len(results) == 2
            assert isinstance(results[0], dict)
            assert 'index' in results[0]
            assert 'score' in results[0]
            assert 'text' in results[0]
            
            # 前两个文档应该更相关
            assert results[0]['index'] in [0, 1]
            assert results[1]['index'] in [0, 1]
    
    @pytest.mark.asyncio
    async def test_semantic_search_empty_documents(self, service):
        """测试空文档列表"""
        with patch.object(service, 'embed_text', return_value=[1.0, 0.0, 0.0]):
            results = await service.semantic_search("查询", [], top_k=5)
            
            assert len(results) == 0
    
    @pytest.mark.asyncio
    async def test_semantic_search_top_k(self, service):
        """测试top_k参数"""
        query = "测试"
        documents = ["文档1", "文档2", "文档3", "文档4", "文档5"]
        
        async def mock_embed_text(text):
            return [1.0, 0.0, 0.0]
        
        with patch.object(service, 'embed_text', side_effect=mock_embed_text):
            results = await service.semantic_search(query, documents, top_k=3)
            
            assert len(results) == 3
    
    @pytest.mark.asyncio
    async def test_semantic_search_sorting(self, service):
        """测试结果按相似度排序"""
        query = "测试"
        documents = ["文档1", "文档2", "文档3"]
        
        call_count = [0]
        
        async def mock_embed_text(text):
            call_count[0] += 1
            # query返回基准向量
            if call_count[0] == 1:
                return [1.0, 0.0, 0.0]
            # 文档返回不同相似度的向量
            elif call_count[0] == 2:
                return [0.5, 0.0, 0.0]  # 相似度中等
            elif call_count[0] == 3:
                return [1.0, 0.0, 0.0]  # 相似度最高
            else:
                return [0.1, 0.0, 0.0]  # 相似度最低
        
        with patch.object(service, 'embed_text', side_effect=mock_embed_text):
            results = await service.semantic_search(query, documents, top_k=3)
            
            # 验证结果按相似度降序排列
            assert results[0]['score'] >= results[1]['score']
            assert results[1]['score'] >= results[2]['score']
    
    @pytest.mark.asyncio
    async def test_semantic_search_with_empty_doc(self, service):
        """测试包含空文档的搜索"""
        query = "测试"
        documents = ["文档1", "", "文档3", None]
        
        async def mock_embed_text(text):
            return [1.0, 0.0, 0.0]
        
        with patch.object(service, 'embed_text', side_effect=mock_embed_text):
            results = await service.semantic_search(query, documents, top_k=5)
            
            # 空文档应该被跳过
            assert all(r['text'] for r in results)
    
    @pytest.mark.asyncio
    async def test_semantic_search_error(self, service):
        """测试语义搜索错误处理"""
        with patch.object(service, 'embed_text', side_effect=Exception("Embedding error")):
            with pytest.raises(Exception) as exc_info:
                await service.semantic_search("查询", ["文档1"], top_k=1)
            
            assert "语义搜索失败" in str(exc_info.value)


class TestAIServiceIntegration:
    """AI服务集成测试"""
    
    @pytest.mark.asyncio
    async def test_provider_switching(self):
        """测试AI提供商切换"""
        with patch('app.services.ai_service.settings') as mock_settings:
            # 测试智谱AI
            mock_settings.AI_PROVIDER = 'zhipu'
            mock_settings.ZHIPU_API_KEY = 'test_key'
            service1 = AIService()
            assert service1.provider == 'zhipu'
            
            # 测试通义千问
            mock_settings.AI_PROVIDER = 'tongyi'
            mock_settings.TONGYI_API_KEY = 'test_key'
            service2 = AIService()
            assert service2.provider == 'tongyi'
    
    @pytest.mark.asyncio
    async def test_embedding_dimension_consistency(self):
        """测试向量维度一致性"""
        service = AIService()
        service.provider = 'zhipu'
        
        mock_response = Mock()
        mock_response.data = [Mock(embedding=[0.1] * 1536)]
        
        with patch.object(service.client.embeddings, 'create', return_value=mock_response):
            result1 = await service.embed_text("文本1")
            result2 = await service.embed_text("文本2")
            
            # 同一提供商的向量维度应该一致
            assert len(result1) == len(result2)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
