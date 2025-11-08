"""AI Service 单元测试"""
import pytest
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.ai_service import AIService
from app.core.config import settings


@pytest.fixture(autouse=True)
def restore_settings():
    """测试结束后还原设置"""
    snapshot = {
        "AI_PROVIDER": settings.AI_PROVIDER,
        "OPENAI_API_KEY": settings.OPENAI_API_KEY,
        "OPENAI_MODEL": settings.OPENAI_MODEL,
        "TONGYI_API_KEY": settings.TONGYI_API_KEY,
        "TONGYI_MODEL": settings.TONGYI_MODEL,
        "WENXIN_API_KEY": settings.WENXIN_API_KEY,
        "WENXIN_SECRET_KEY": settings.WENXIN_SECRET_KEY,
        "WENXIN_MODEL": settings.WENXIN_MODEL,
        "ZHIPU_API_KEY": settings.ZHIPU_API_KEY,
        "ZHIPU_MODEL": settings.ZHIPU_MODEL,
    }
    yield
    for key, value in snapshot.items():
        setattr(settings, key, value)


def _mock_httpx_client(*, post_payload=None, get_payload=None):
    """构造AsyncClient的mock对象"""
    client = AsyncMock()
    client.__aenter__.return_value = client
    client.__aexit__.return_value = None

    if post_payload is not None:
        post_response = MagicMock()
        post_response.json.return_value = post_payload
        post_response.raise_for_status.return_value = None
        client.post = AsyncMock(return_value=post_response)

    if get_payload is not None:
        get_response = MagicMock()
        get_response.json.return_value = get_payload
        get_response.raise_for_status.return_value = None
        client.get = AsyncMock(return_value=get_response)

    return client


@pytest.mark.asyncio
async def test_openai_generate_text():
    settings.AI_PROVIDER = "openai"
    settings.OPENAI_API_KEY = "test-key"
    service = AIService()

    mock_response = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content="OpenAI响应"))],
        usage=SimpleNamespace(total_tokens=10),
    )

    with patch(
        "openai.ChatCompletion.acreate",
        new=AsyncMock(return_value=mock_response)
    ) as mock_api:
        result = await service.generate_text("测试提示词")

    assert result == "OpenAI响应"
    mock_api.assert_awaited_once()


@pytest.mark.asyncio
async def test_tongyi_generate_text():
    settings.AI_PROVIDER = "tongyi"
    settings.TONGYI_API_KEY = "tongyi-key"
    service = AIService()

    # Mock dashscope.Generation.call
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.output = {
        "choices": [
            {"message": {"content": [{"text": "通义响应"}]}}
        ]
    }
    mock_response.usage = {"total_tokens": 20}

    with patch("app.services.ai_service.dashscope.Generation.call", return_value=mock_response):
        result = await service.generate_text("测试提示词")

    assert result == "通义响应"


@pytest.mark.asyncio
async def test_wenxin_generate_text():
    settings.AI_PROVIDER = "wenxin"
    settings.WENXIN_API_KEY = "wenxin-key"
    settings.WENXIN_SECRET_KEY = "wenxin-secret"
    service = AIService()

    # Mock erniebot.ChatCompletion.create
    mock_response = MagicMock()
    mock_response.result = "文心响应"
    mock_response.usage = {"total_tokens": 15}

    with patch("app.services.ai_service.erniebot.ChatCompletion.create", return_value=mock_response):
        result = await service.generate_text("测试提示词")

    assert result == "文心响应"


@pytest.mark.asyncio
async def test_fetch_wenxin_access_token():
    settings.AI_PROVIDER = "wenxin"
    settings.WENXIN_API_KEY = "wenxin-key"
    settings.WENXIN_SECRET_KEY = "wenxin-secret"
    service = AIService()

    payload = {"access_token": "new-token", "expires_in": 3600}
    mock_client = _mock_httpx_client(get_payload=payload)

    with patch("httpx.AsyncClient", return_value=mock_client):
        token = await service._get_wenxin_access_token()

    assert token == "new-token"


@pytest.mark.asyncio
async def test_zhipu_generate_text():
    settings.AI_PROVIDER = "zhipu"
    settings.ZHIPU_API_KEY = "glm-key"
    service = AIService()

    payload = {"choices": [{"message": {"content": "智谱响应"}}], "usage": {"total_tokens": 18}}
    mock_client = _mock_httpx_client(post_payload=payload)

    with patch("httpx.AsyncClient", return_value=mock_client):
        result = await service.generate_text("测试提示词")

    assert result == "智谱响应"


@pytest.mark.asyncio
async def test_embed_text_openai():
    settings.AI_PROVIDER = "openai"
    settings.OPENAI_API_KEY = "test-key"
    service = AIService()

    mock_embedding = {"data": [{"embedding": [0.1, 0.2, 0.3]}]}

    with patch(
        "openai.Embedding.acreate",
        new=AsyncMock(return_value=mock_embedding)
    ):
        result = await service.embed_text("测试文本")

    assert result == [0.1, 0.2, 0.3]


@pytest.mark.asyncio
async def test_generate_text_unsupported_provider():
    settings.AI_PROVIDER = "unknown"
    service = AIService()

    with pytest.raises(ValueError):
        await service.generate_text("测试")
