"""AI服务Mock测试"""
import pytest
from unittest.mock import Mock, patch
from app.services.ai_service import AIService

@pytest.fixture
def mock_ai_service():
    """创建Mock AI服务"""
    with patch('app.services.ai_service.AIService') as mock_service:
        service = Mock()
        service.generate_text.return_value = {"content": "测试回复", "model": "test-model"}
        service.embed_text.return_value = [0.1, 0.2, 0.3]
        mock_service.return_value = service
        yield service

class TestAIServiceMock:
    """AI服务Mock测试"""
    
    def test_generate_text_mock(self, mock_ai_service):
        """测试文本生成Mock"""
        result = mock_ai_service.generate_text("测试内容", "test")
        assert result["content"] == "测试回复"
        assert result["model"] == "test-model"
        mock_ai_service.generate_text.assert_called_once_with("测试内容", "test")
    
    def test_embed_text_mock(self, mock_ai_service):
        """测试文本嵌入Mock"""
        result = mock_ai_service.embed_text("测试文本")
        assert result == [0.1, 0.2, 0.3]
        mock_ai_service.embed_text.assert_called_once_with("测试文本")
