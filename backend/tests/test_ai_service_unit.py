"""
AI Service 单元测试
测试AI服务的核心功能，包括向量化、语义搜索等
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
import numpy as np
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.services.ai_service import ai_service
from app.core.config import settings


@pytest.fixture
def mock_zhipu_response():
    """模拟智谱AI的响应"""
    return {
        "choices": [{"message": {"content": "生成的文本内容"}}],
        "usage": {"total_tokens": 100}
    }


@pytest.fixture
def mock_embedding_response():
    """模拟向量化的响应"""
    return [0.1, 0.2, 0.3, 0.4, 0.5] * 30  # 150维向量


@pytest.mark.asyncio
async def test_zhipu_generate_text(mock_zhipu_response):
    """测试智谱AI文本生成"""
    with patch('httpx.AsyncClient.post') as mock_post:
        mock_post.return_value = Mock()
        mock_post.return_value.json = Mock(return_value=mock_zhipu_response)

        result = await ai_service._zhipu_generate_text(
            prompt="测试提示词",
            max_tokens=100
        )

        assert result == "生成的文本内容"
        mock_post.assert_called_once()


@pytest.mark.asyncio
async def test_zhipu_embed_text(mock_embedding_response):
    """测试智谱AI向量化"""
    with patch('httpx.AsyncClient.post') as mock_post:
        mock_post.return_value = Mock()
        mock_post.return_value.json = Mock(return_value={
            "data": [{"embedding": mock_embedding_response[:4]}]
        })

        result = await ai_service._zhipu_embed_text("测试文本")

        assert isinstance(result, list)
        assert len(result) > 0
        mock_post.assert_called_once()


@pytest.mark.asyncio
async def test_openai_generate_text():
    """测试OpenAI文本生成"""
    with patch('openai.OpenAI') as mock_client:
        mock_completion = Mock()
        mock_completion.choices = [Mock()]
        mock_completion.choices[0].message.content = "OpenAI生成的文本"

        mock_client.return_value.chat.completions.create = Mock(return_value=mock_completion)

        result = await ai_service._openai_generate_text(
            prompt="测试提示词",
            max_tokens=100
        )

        assert result == "OpenAI生成的文本"


@pytest.mark.asyncio
async def test_openai_embed_text(mock_embedding_response):
    """测试OpenAI向量化"""
    with patch('openai.OpenAI') as mock_client:
        mock_response = Mock()
        mock_response.data = [Mock()]
        mock_response.data[0].embedding = mock_embedding_response[:4]

        mock_client.return_value.embeddings.create = Mock(return_value=mock_response)

        result = await ai_service._openai_embed_text("测试文本")

        assert isinstance(result, list)
        assert len(result) > 0


@pytest.mark.asyncio
async def test_generate_text_with_cache():
    """测试AI文本生成并缓存结果"""
    with patch.object(ai_service, '_zhipu_generate_text', new_callable=AsyncMock) as mock_zhipu, \
         patch('app.services.cache_service.cache_service.cache_ai_response') as mock_cache:

        mock_zhipu.return_value = "缓存的AI响应"

        result = await ai_service.generate_text(
            prompt="测试提示词",
            use_cache=True
        )

        assert result == "缓存的AI响应"
        mock_cache.assert_called_once()


@pytest.mark.asyncio
async def test_semantic_search():
    """测试语义搜索功能"""
    documents = [
        {"id": 1, "content": "这是一篇关于金融的文档"},
        {"id": 2, "content": "这是一篇关于科技的文档"},
        {"id": 3, "content": "这是一篇关于金融科技的文档"}
    ]

    with patch.object(ai_service, 'embed_text', new_callable=AsyncMock) as mock_embed:
        # 模拟向量化结果
        mock_embed.side_effect = [
            [0.1, 0.2, 0.3] * 50,  # "金融" 相关
            [0.8, 0.9, 0.1] * 50,  # "科技" 相关
            [0.3, 0.5, 0.6] * 50,  # "金融科技" 相关
        ]

        results = await ai_service.semantic_search(
            query="金融",
            documents=documents,
            top_k=2
        )

        assert len(results) == 2
        assert all(isinstance(r['score'], float) for r in results)


@pytest.mark.asyncio
async def test_provider_swiching():
    """测试AI提供商切换功能"""
    # 测试切换到OpenAI
    original_provider = ai_service.provider

    ai_service.provider = "openai"

    with patch('openai.OpenAI') as mock_client:
        mock_completion = Mock()
        mock_completion.choices = [Mock()]
        mock_completion.choices[0].message.content = "OpenAI生成的内容"
        mock_client.return_value.chat.completions.create = Mock(return_value=mock_completion)

        result = await ai_service.generate_text(prompt="测试")

        assert result == "OpenAI生成的内容"

    # 恢复原始提供商
    ai_service.provider = original_provider


@pytest.mark.asyncio
async def test_empty_text_embedding():
    """测试空文本向量化处理"""
    result = await ai_service.embed_text("")

    assert isinstance(result, list)
    assert len(result) > 0
    assert all(isinstance(x, float) for x in result)


@pytest.mark.asyncio
async def test_long_text_embedding():
    """测试长文本向量化处理"""
    long_text = "测试文本 " * 1000  # 约2000个字符

    with patch.object(ai_service, '_zhipu_embed_text', new_callable=AsyncMock) as mock_embed:
        mock_embed.return_value = [0.1] * 150

        result = await ai_service.embed_text(long_text)

        assert isinstance(result, list)
        assert len(result) == 150


@pytest.mark.asyncio
async def test_api_error_handling():
    """测试API错误处理"""
    with patch('httpx.AsyncClient.post') as mock_post:
        mock_post.side_effect = Exception("API连接失败")

        with pytest.raises(Exception) as exc_info:
            await ai_service._zhipu_generate_text(prompt="测试")

        assert "API连接失败" in str(exc_info.value)


@pytest.mark.asyncio
async def test_embedding_dimension_consistency():
    """测试向量化维度一致性"""
    test_texts = ["测试1", "测试2", "测试3"]

    with patch('httpx.AsyncClient.post') as mock_post:
        mock_post.return_value = Mock()
        mock_post.return_value.json = Mock(return_value={
            "data": [{"embedding": [0.1, 0.2, 0.3, 0.4]}]
        })

        embeddings = []
        for text in test_texts:
            embedding = await ai_service._zhipu_embed_text(text)
            embeddings.append(embedding)

        # 验证所有向量维度相同
        dimensions = [len(e) for e in embeddings]
        assert len(set(dimensions)) == 1  # 所有维度一致


@pytest.mark.asyncio
async def test_unsupported_provider():
    """测试不支持的AI提供商"""
    ai_service.provider = "unsupported_provider"

    with pytest.raises(Exception) as exc_info:
        await ai_service.embed_text("测试")

    assert "不支持的AI提供商或向量化方法未实现" in str(exc_info.value)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
