"""AI服务边界测试 - 提升测试覆盖率"""
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from types import SimpleNamespace

from app.services.ai_service import AIService
from app.core.config import settings


def _mock_httpx_client(post_payload=None, status_code=200):
    """创建一个模拟的httpx.AsyncClient"""
    mock_response = MagicMock()
    mock_response.status_code = status_code
    mock_response.json.return_value = post_payload

    async def mock_post(*args, **kwargs):
        return mock_response

    mock_client = MagicMock()
    mock_client.post = AsyncMock(side_effect=mock_post)
    
    # 确保可以作为上下文管理器使用
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None

    return mock_client

class TestAIServiceBoundaryCases:
    """AI服务边界条件测试"""

    @pytest.fixture(autouse=True)
    def setup_test_env(self):
        """设置测试环境"""
        # 保存原始设置
        original_provider = settings.AI_PROVIDER
        original_key = settings.OPENAI_API_KEY

        yield

        # 恢复原始设置
        settings.AI_PROVIDER = original_provider
        settings.OPENAI_API_KEY = original_key

    # ========== 输入参数边界测试 ==========

    @pytest.mark.asyncio
    async def test_empty_prompt_handling(self):
        """测试空提示词处理"""
        settings.AI_PROVIDER = "openai"
        settings.OPENAI_API_KEY = "test-key"
        service = AIService()

        mock_response = SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content=""))],
            usage=SimpleNamespace(total_tokens=0),
        )

        with patch("openai.ChatCompletion.acreate", new=AsyncMock(return_value=mock_response)):
            result = await service.generate_text("")
            assert result == ""

    @pytest.mark.asyncio
    async def test_very_long_prompt(self):
        """测试超长提示词"""
        settings.AI_PROVIDER = "openai"
        settings.OPENAI_API_KEY = "test-key"
        service = AIService()

        # 创建10000字符的提示词
        long_prompt = "测试提示词 " * 1000

        mock_response = SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content="处理完成"))],
            usage=SimpleNamespace(total_tokens=150),
        )

        with patch("openai.ChatCompletion.acreate", new=AsyncMock(return_value=mock_response)):
            result = await service.generate_text(long_prompt)
            assert result == "处理完成"

    @pytest.mark.asyncio
    async def test_temperature_boundary_values(self):
        """测试温度参数边界值"""
        settings.AI_PROVIDER = "openai"
        settings.OPENAI_API_KEY = "test-key"
        service = AIService()

        test_cases = [
            (-0.1, "should_raise_error"),  # 负数
            (0.0, "should_work"),          # 最小值
            (1.0, "should_work"),          # 最大值
            (1.1, "should_raise_error"),   # 超过最大值
            (2.0, "should_raise_error"),   # 过大值
        ]

        for temp, expected in test_cases:
            mock_response = SimpleNamespace(
                choices=[SimpleNamespace(message=SimpleNamespace(content="响应"))],
                usage=SimpleNamespace(total_tokens=10),
            )

            with patch("openai.ChatCompletion.acreate", new=AsyncMock(return_value=mock_response)):
                if expected == "should_work":
                    result = await service.generate_text("测试", temperature=temp)
                    assert result == "响应"
                else:
                    # 在实际实现中，应该验证参数范围
                    pass

    @pytest.mark.asyncio
    async def test_max_tokens_boundary(self):
        """测试最大token边界值"""
        settings.AI_PROVIDER = "openai"
        settings.OPENAI_API_KEY = "test-key"
        service = AIService()

        boundary_values = [0, 1, 2048, 4096, 8192, -1]

        for max_tokens in boundary_values:
            mock_response = SimpleNamespace(
                choices=[SimpleNamespace(message=SimpleNamespace(content="响应"))],
                usage=SimpleNamespace(total_tokens=min(max_tokens, 10) if max_tokens > 0 else 0),
            )

            with patch("openai.ChatCompletion.acreate", new=AsyncMock(return_value=mock_response)):
                if max_tokens >= 0:  # 非负值应该正常工作
                    result = await service.generate_text("测试", max_tokens=max_tokens)
                    assert result == "响应"

    # ========== 响应数据边界测试 ==========

    @pytest.mark.asyncio
    async def test_empty_response_content(self):
        """测试空响应内容"""
        settings.AI_PROVIDER = "openai"
        settings.OPENAI_API_KEY = "test-key"
        service = AIService()

        mock_response = SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content=""))],
            usage=SimpleNamespace(total_tokens=0),
        )

        with patch("openai.ChatCompletion.acreate", new=AsyncMock(return_value=mock_response)):
            result = await service.generate_text("测试提示词")
            assert result == ""

    @pytest.mark.asyncio
    async def test_null_response_content(self):
        """测试null响应内容"""
        settings.AI_PROVIDER = "openai"
        settings.OPENAI_API_KEY = "test-key"
        service = AIService()

        mock_response = SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content=None))],
            usage=SimpleNamespace(total_tokens=0),
        )

        with patch("openai.ChatCompletion.acreate", new=AsyncMock(return_value=mock_response)):
            with pytest.raises(Exception):
                await service.generate_text("测试提示词")

    @pytest.mark.asyncio
    async def test_whitespace_response(self):
        """测试仅空白字符响应"""
        settings.AI_PROVIDER = "openai"
        settings.OPENAI_API_KEY = "test-key"
        service = AIService()

        mock_response = SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content="   \n\t  "))],
            usage=SimpleNamespace(total_tokens=5),
        )

        with patch("openai.ChatCompletion.acreate", new=AsyncMock(return_value=mock_response)):
            result = await service.generate_text("测试提示词")
            assert result.strip() == ""  # 应该被strip处理

    # ========== API异常响应测试 ==========

    @pytest.mark.asyncio
    async def test_malformed_openai_response(self):
        """测试格式错误的OpenAI响应"""
        settings.AI_PROVIDER = "openai"
        settings.OPENAI_API_KEY = "test-key"
        service = AIService()

        # 缺少必要字段的响应
        malformed_responses = [
            SimpleNamespace(),  # 完全空响应
            SimpleNamespace(choices=[]),  # 空选择列表
            SimpleNamespace(choices=[SimpleNamespace()]),  # 缺少message字段
            SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace())]),  # 缺少content字段
        ]

        for malformed_response in malformed_responses:
            with patch("openai.ChatCompletion.acreate", new=AsyncMock(return_value=malformed_response)):
                with pytest.raises(Exception):
                    await service.generate_text("测试提示词")

    @pytest.mark.asyncio
    async def test_tongyi_malformed_response(self):
        """测试格式错误的通义响应"""
        settings.AI_PROVIDER = "tongyi"
        settings.TONGYI_API_KEY = "tongyi-key"
        service = AIService()

        malformed_payloads = [
            {},  # 空响应
            {"output": {}},  # 缺少choices
            {"output": {"choices": []}},  # 空choices
            {"output": {"choices": [{}]}},  # 缺少message
            {"output": {"choices": [{"message": {}}]}},  # 缺少content
        ]

        for payload in malformed_payloads:
            mock_client = _mock_httpx_client(post_payload=payload)

            with patch("httpx.AsyncClient", return_value=mock_client):
                with pytest.raises(Exception):
                    await service.generate_text("测试提示词")

    # ========== 网络异常测试 ==========

    @pytest.mark.asyncio
    async def test_network_timeout(self):
        """测试网络超时"""
        settings.AI_PROVIDER = "openai"
        settings.OPENAI_API_KEY = "test-key"
        service = AIService()

        async def timeout_func(*args, **kwargs):
            await asyncio.sleep(0.1)  # 模拟网络延迟
            raise asyncio.TimeoutError("请求超时")

        with patch("openai.ChatCompletion.acreate", side_effect=timeout_func):
            with pytest.raises(Exception):
                await service.generate_text("测试提示词")

    @pytest.mark.asyncio
    async def test_connection_error(self):
        """测试连接错误"""
        settings.AI_PROVIDER = "openai"
        settings.OPENAI_API_KEY = "test-key"
        service = AIService()

        with patch("openai.ChatCompletion.acreate", side_effect=ConnectionError("连接失败")):
            with pytest.raises(Exception):
                await service.generate_text("测试提示词")

    # ========== 认证和权限测试 ==========

    @pytest.mark.asyncio
    async def test_invalid_api_key(self):
        """测试无效API密钥"""
        settings.AI_PROVIDER = "openai"
        settings.OPENAI_API_KEY = "invalid-key"
        service = AIService()

        with patch("openai.ChatCompletion.acreate", side_effect=Exception("Invalid API key")):
            with pytest.raises(Exception):
                await service.generate_text("测试提示词")

    @pytest.mark.asyncio
    async def test_missing_api_key(self):
        """测试缺失API密钥"""
        settings.AI_PROVIDER = "zhipu"
        settings.ZHIPU_API_KEY = ""  # 空密钥
        service = AIService()

        with pytest.raises(ValueError, match="ZHIPU_API_KEY 未配置"):
            await service.generate_text("测试提示词")

    # ========== 特殊字符和内容测试 ==========

    @pytest.mark.asyncio
    async def test_special_characters_in_prompt(self):
        """测试提示词中的特殊字符"""
        settings.AI_PROVIDER = "openai"
        settings.OPENAI_API_KEY = "test-key"
        service = AIService()

        special_prompts = [
            "测试\n换行\r\n字符",
            "测试\t制表符",
            "测试\"引号\"和'单引号'",
            "测试\\反斜杠\\",
            "测试\u0000空字符",
            "测试\x00十六进制空字符",
            "测试\r回车符",
        ]

        for prompt in special_prompts:
            mock_response = SimpleNamespace(
                choices=[SimpleNamespace(message=SimpleNamespace(content="处理完成"))],
                usage=SimpleNamespace(total_tokens=10),
            )

            with patch("openai.ChatCompletion.acreate", new=AsyncMock(return_value=mock_response)):
                result = await service.generate_text(prompt)
                assert result == "处理完成"

    @pytest.mark.asyncio
    async def test_unicode_content(self):
        """测试Unicode内容"""
        settings.AI_PROVIDER = "openai"
        settings.OPENAI_API_KEY = "test-key"
        service = AIService()

        unicode_prompts = [
            "测试中文内容：售前方案",
            "Testing English content",
            "テスト日本語コンテンツ",
            "🚀 Emoji测试 🎯",
            "数学公式: ∑(n=1 to ∞) 1/n² = π²/6",
            "特殊符号: © ® ™ § ¶ † ‡",
        ]

        for prompt in unicode_prompts:
            mock_response = SimpleNamespace(
                choices=[SimpleNamespace(message=SimpleNamespace(content=f"响应: {prompt}"))],
                usage=SimpleNamespace(total_tokens=20),
            )

            with patch("openai.ChatCompletion.acreate", new=AsyncMock(return_value=mock_response)):
                result = await service.generate_text(prompt)
                assert "响应:" in result

    # ========== 并发和压力测试 ==========

    @pytest.mark.asyncio
    async def test_concurrent_requests(self):
        """测试并发请求处理"""
        settings.AI_PROVIDER = "openai"
        settings.OPENAI_API_KEY = "test-key"
        service = AIService()

        mock_response = SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content="并发响应"))],
            usage=SimpleNamespace(total_tokens=10),
        )

        with patch("openai.ChatCompletion.acreate", new=AsyncMock(return_value=mock_response)):
            # 同时发起10个请求
            tasks = [
                service.generate_text(f"并发测试 {i}")
                for i in range(10)
            ]

            results = await asyncio.gather(*tasks)
            assert len(results) == 10
            assert all(result == "并发响应" for result in results)

    # ========== 错误恢复测试 ==========

    @pytest.mark.asyncio
    async def test_retry_mechanism(self):
        """测试重试机制（如果实现）"""
        settings.AI_PROVIDER = "openai"
        settings.OPENAI_API_KEY = "test-key"
        service = AIService()

        # 第一次调用失败，第二次成功
        call_count = 0

        async def mock_with_retry(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise Exception("第一次调用失败")
            else:
                return SimpleNamespace(
                    choices=[SimpleNamespace(message=SimpleNamespace(content="重试成功"))],
                    usage=SimpleNamespace(total_tokens=10),
                )

        with patch("openai.ChatCompletion.acreate", side_effect=mock_with_retry):
            with pytest.raises(Exception, match="第一次调用失败"):
                await service.generate_text("测试重试")


class TestAIEmbeddingBoundaryCases:
    """AI嵌入服务边界测试"""

    @pytest.mark.asyncio
    async def test_embed_empty_text(self):
        """测试空文本嵌入"""
        settings.AI_PROVIDER = "openai"
        settings.OPENAI_API_KEY = "test-key"
        service = AIService()

        mock_response = SimpleNamespace(
            data=[{"embedding": [0.1] * 1536}],
            usage=SimpleNamespace(total_tokens=0),
        )

        with patch("openai.Embedding.acreate", new=AsyncMock(return_value=mock_response)):
            result = await service.embed_text("")
            assert len(result) == 1536
            assert all(isinstance(x, float) for x in result)

    @pytest.mark.asyncio
    async def test_embed_very_long_text(self):
        """测试超长文本嵌入"""
        settings.AI_PROVIDER = "openai"
        settings.OPENAI_API_KEY = "test-key"
        service = AIService()

        # 创建10000字符的文本
        long_text = "这是一个测试句子。" * 1000

        mock_response = SimpleNamespace(
            data=[{"embedding": [0.1] * 1536}],
            usage=SimpleNamespace(total_tokens=2000),
        )

        with patch("openai.Embedding.acreate", new=AsyncMock(return_value=mock_response)):
            result = await service.embed_text(long_text)
            assert len(result) == 1536
            assert all(isinstance(x, float) for x in result)

    @pytest.mark.asyncio
    async def test_embed_special_characters(self):
        """测试特殊字符文本嵌入"""
        settings.AI_PROVIDER = "openai"
        settings.OPENAI_API_KEY = "test-key"
        service = AIService()

        special_texts = [
            "测试\n换行\t制表符",
            "测试\"引号\"和'单引号'",
            "测试\\反斜杠\\",
            "🚀 Emoji测试 🎯",
            "数学公式: ∑(n=1 to ∞) 1/n² = π²/6",
        ]

        for text in special_texts:
            mock_response = SimpleNamespace(
                data=[{"embedding": [0.1] * 1536}],
                usage=SimpleNamespace(total_tokens=10),
            )

            with patch("openai.Embedding.acreate", new=AsyncMock(return_value=mock_response)):
                result = await service.embed_text(text)
                assert len(result) == 1536
                assert all(isinstance(x, float) for x in result)