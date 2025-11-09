"""服务和工具测试 - 提升覆盖率"""
import pytest
import io
import tempfile
import os
from unittest.mock import Mock, patch
from app.services.ai_service import AIService
from app.services.cache_service import CacheService
from app.services.document_processor import DocumentProcessor
from app.services.export_service import ExportService
from app.services.template_service import TemplateService
from app.services.vector_service import VectorService
from app.services.websocket_manager import WebSocketManager
from app.utils.security_utils import sanitize_for_api, XSSProtector
from app.utils.diff_utils import DiffUtils


class TestAIServiceExtended:
    """扩展AI服务测试"""

    def test_ai_service_init(self):
        """测试AI服务初始化"""
        service = AIService()
        assert hasattr(service, 'provider')
        assert hasattr(service, 'client')

    def test_generate_text_success(self):
        """测试生成文本成功"""
        service = AIService()
        with patch.object(service, '_generate_with_openai') as mock_generate:
            mock_generate.return_value = "生成的内容"
            result = service.generate_text("测试提示")
            assert result == "生成的内容"

    def test_generate_text_fallback(self):
        """测试生成文本回退机制"""
        service = AIService()
        original_provider = service.provider
        service.provider = "zhipu"
        
        with patch.object(service, '_generate_with_zhipu') as mock_zhipu, \
             patch.object(service, '_generate_with_openai') as mock_openai:
            mock_zhipu.side_effect = Exception("Zhipu error")
            mock_openai.return_value = "回退内容"
            result = service.generate_text("测试提示")
            assert result == "回退内容"
        
        # 恢复原始提供商
        service.provider = original_provider

    def test_embed_text_success(self):
        """测试文本嵌入成功"""
        service = AIService()
        with patch.object(service, '_embed_with_openai') as mock_embed:
            mock_embed.return_value = [0.1, 0.2, 0.3]
            result = service.embed_text("测试文本")
            assert result == [0.1, 0.2, 0.3]

    def test_provider_switch(self):
        """测试提供商切换"""
        service = AIService()
        original_provider = service.provider
        
        service.provider = "openai"
        assert service.provider == "openai"
        
        # 恢复原始提供商
        service.provider = original_provider


class TestCacheServiceExtended:
    """扩展缓存服务测试"""

    def test_cache_service_init(self):
        """测试缓存服务初始化"""
        service = CacheService()
        assert hasattr(service, 'redis_client')
        assert hasattr(service, 'memory_cache')

    def test_set_get_cache(self):
        """测试缓存设置和获取"""
        service = CacheService()
        service.set("test_key", "test_value", ttl=60)
        result = service.get("test_key")
        assert result == "test_value"

    def test_cache_delete(self):
        """测试缓存删除"""
        service = CacheService()
        service.set("test_key", "test_value")
        service.delete("test_key")
        result = service.get("test_key")
        assert result is None

    def test_cache_clear_pattern(self):
        """测试模式清除缓存"""
        service = CacheService()
        service.set("test:1", "value1")
        service.set("test:2", "value2")
        service.set("other:1", "value3")
        
        service.clear_pattern("test:*")
        
        assert service.get("test:1") is None
        assert service.get("test:2") is None
        assert service.get("other:1") == "value3"

    def test_cache_stats(self):
        """测试缓存统计"""
        service = CacheService()
        stats = service.get_stats()
        assert isinstance(stats, dict)
        assert "memory_size" in stats


class TestDocumentProcessorExtended:
    """扩展文档处理器测试"""

    def test_extract_text_txt(self):
        """测试TXT文件文本提取"""
        processor = DocumentProcessor()
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write("这是测试文本内容")
            temp_path = f.name
        
        try:
            result = processor.extract_text(temp_path)
            assert "这是测试文本内容" in result
        finally:
            os.unlink(temp_path)

    def test_extract_text_empty_file(self):
        """测试空文件文本提取"""
        processor = DocumentProcessor()
        
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
            temp_path = f.name
        
        try:
            result = processor.extract_text(temp_path)
            assert result == ""
        finally:
            os.unlink(temp_path)

    def test_extract_text_unsupported_format(self):
        """测试不支持的格式"""
        processor = DocumentProcessor()
        result = processor.extract_text("test.xyz")
        assert result == ""

    def test_validate_file_type_txt(self):
        """测试TXT文件类型验证"""
        processor = DocumentProcessor()
        assert processor.validate_file_type("test.txt") == True
        assert processor.validate_file_type("test.docx") == True
        assert processor.validate_file_type("test.xyz") == False


class TestExportServiceExtended:
    """扩展导出服务测试"""

    def test_export_to_word(self):
        """测试导出到Word"""
        service = ExportService()
        content = "测试内容\n标题"
        
        with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as f:
            temp_path = f.name
        
        try:
            result = service.export_to_word(content, temp_path)
            assert result == temp_path
            assert os.path.exists(temp_path)
            assert os.path.getsize(temp_path) > 0
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_export_to_excel(self):
        """测试导出到Excel"""
        service = ExportService()
        data = [
            {"姓名": "张三", "年龄": 25, "城市": "北京"},
            {"姓名": "李四", "年龄": 30, "城市": "上海"}
        ]
        
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as f:
            temp_path = f.name
        
        try:
            result = service.export_to_excel(data, temp_path)
            assert result == temp_path
            assert os.path.exists(temp_path)
            assert os.path.getsize(temp_path) > 0
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_split_markdown_text(self):
        """测试Markdown文本分割"""
        service = ExportService()
        content = "# 标题1\n内容1\n\n# 标题2\n内容2"
        
        parts = service.split_markdown_text(content)
        assert len(parts) >= 2
        assert any("标题1" in part for part in parts)
        assert any("标题2" in part for part in parts)


class TestTemplateServiceExtended:
    """扩展模板服务测试"""

    def test_render_template_simple(self):
        """测试简单模板渲染"""
        service = TemplateService()
        template = "你好，{{ name }}！欢迎来到{{ place }}。"
        variables = {"name": "张三", "place": "北京"}
        
        result = service.render_template(template, variables)
        assert "你好，张三！" in result
        assert "欢迎来到北京" in result

    def test_render_template_missing_variable(self):
        """测试缺失变量处理"""
        service = TemplateService()
        template = "你好，{{ name }}！"
        variables = {}
        
        result = service.render_template(template, variables)
        assert "你好，" in result

    def test_extract_template_variables(self):
        """测试提取模板变量"""
        service = TemplateService()
        template = "你好，{{ name }}！来自{{ city }}的{{ age }}岁用户"
        
        variables = service.extract_variables(template)
        assert "name" in variables
        assert "city" in variables
        assert "age" in variables

    def test_validate_template_syntax(self):
        """测试模板语法验证"""
        service = TemplateService()
        
        # 有效模板
        valid_template = "你好，{{ name }}！"
        assert service.validate_template(valid_template) == True
        
        # 无效模板
        invalid_template = "你好，{{ name ！"
        assert service.validate_template(invalid_template) == False


class TestVectorServiceExtended:
    """扩展向量服务测试"""

    def test_vector_similarity_cosine(self):
        """测试余弦相似度计算"""
        service = VectorService()
        
        vec1 = [1, 0, 0]
        vec2 = [0, 1, 0]
        vec3 = [1, 0, 0]
        
        # 相似向量
        sim1 = service.cosine_similarity(vec1, vec3)
        assert abs(sim1 - 1.0) < 0.001
        
        # 正交向量
        sim2 = service.cosine_similarity(vec1, vec2)
        assert abs(sim2 - 0.0) < 0.001

    def test_normalize_vector(self):
        """测试向量归一化"""
        service = VectorService()
        
        vec = [3, 4]
        normalized = service.normalize_vector(vec)
        
        expected_length = 5.0  # sqrt(3^2 + 4^2)
        assert abs(normalized[0] - 0.6) < 0.001  # 3/5
        assert abs(normalized[1] - 0.8) < 0.001  # 4/5

    def test_search_with_similarity_threshold(self):
        """测试相似度阈值搜索"""
        service = VectorService()
        
        query_vec = [1, 0, 0]
        vectors = [
            {"id": 1, "vector": [1, 0, 0], "content": "完全相同"},
            {"id": 2, "vector": [0.9, 0.1, 0], "content": "很相似"},
            {"id": 3, "vector": [0, 1, 0], "content": "不相似"}
        ]
        
        results = service.search_similar(query_vec, vectors, threshold=0.8)
        
        # 应该只返回前两个
        assert len(results) == 2
        assert any(r["id"] == 1 for r in results)
        assert any(r["id"] == 2 for r in results)


class TestWebSocketManagerExtended:
    """扩展WebSocket管理器测试"""

    def test_websocket_manager_init(self):
        """测试WebSocket管理器初始化"""
        manager = WebSocketManager()
        assert hasattr(manager, 'connections')
        assert hasattr(manager, 'user_connections')

    def test_add_connection(self):
        """测试添加连接"""
        manager = WebSocketManager()
        websocket = Mock()
        user_id = 1
        
        manager.add_connection(websocket, user_id)
        assert websocket in manager.connections
        assert user_id in manager.user_connections

    def test_remove_connection(self):
        """测试移除连接"""
        manager = WebSocketManager()
        websocket = Mock()
        user_id = 1
        
        manager.add_connection(websocket, user_id)
        manager.remove_connection(websocket)
        
        assert websocket not in manager.connections
        assert user_id not in manager.user_connections

    def test_broadcast_message(self):
        """测试广播消息"""
        manager = WebSocketManager()
        websocket1 = Mock()
        websocket2 = Mock()
        
        manager.add_connection(websocket1, 1)
        manager.add_connection(websocket2, 2)
        
        message = {"type": "test", "content": "测试消息"}
        manager.broadcast(message)
        
        # 检查是否发送给所有连接
        websocket1.send_json.assert_called_once_with(message)
        websocket2.send_json.assert_called_once_with(message)


class TestSecurityUtilsExtended:
    """扩展安全工具测试"""

    def test_sanitize_html(self):
        """测试HTML清理"""
        content = "<script>alert('xss')</script>安全内容"
        result = XSSProtector.sanitize_html(content)
        assert "<script>" not in result
        assert "安全内容" in result

    def test_sanitize_input(self):
        """测试输入清理"""
        content = "javascript:alert('xss')"
        result = XSSProtector.sanitize_input(content)
        assert "javascript:" not in result

    def test_is_dangerous_content(self):
        """测试危险内容检测"""
        dangerous = "<script>alert('xss')</script>"
        safe = "这是安全的内容"
        
        assert XSSProtector.is_dangerous_content(dangerous) == True
        assert XSSProtector.is_dangerous_content(safe) == False

    def test_validate_url_safe(self):
        """测试安全URL验证"""
        safe_url = "https://example.com"
        dangerous_url = "javascript:alert('xss')"
        
        assert XSSProtector.validate_url(safe_url) == True
        assert XSSProtector.validate_url(dangerous_url) == False

    def test_sanitize_for_api_string(self):
        """测试API数据清理-字符串"""
        content = "<script>alert('xss')</script>"
        result = sanitize_for_api(content)
        assert "<script>" not in result

    def test_sanitize_for_api_dict(self):
        """测试API数据清理-字典"""
        data = {
            "name": "<script>alert('xss')</script>",
            "safe": "安全内容",
            "nested": {"content": "javascript:alert('xss')"}
        }
        result = sanitize_for_api(data)
        
        assert "<script>" not in result["name"]
        assert result["safe"] == "安全内容"
        assert "javascript:" not in result["nested"]["content"]

    def test_sanitize_empty_content(self):
        """测试空内容清理"""
        result = XSSProtector.sanitize_html("")
        assert result == ""

    def test_validate_empty_url(self):
        """测试空URL验证"""
        assert XSSProtector.validate_url("") == True
        assert XSSProtector.validate_url(None) == True


class TestDiffUtilsExtended:
    """扩展差异工具测试"""

    def test_calculate_text_diff_identical(self):
        """测试相同文本差异"""
        text1 = "相同内容"
        text2 = "相同内容"
        
        diff = DiffUtils.calculate_text_diff(text1, text2)
        assert diff["total_changes"] == 0  # 没有差异
        assert diff["similarity_ratio"] == 1.0

    def test_calculate_text_diff_simple(self):
        """测试简单差异"""
        text1 = "原始内容"
        text2 = "修改内容"
        
        diff = DiffUtils.calculate_text_diff(text1, text2)
        assert diff["total_changes"] > 0  # 有差异
        assert diff["similarity_ratio"] < 1.0

    def test_calculate_text_diff_empty(self):
        """测试空文本差异"""
        text1 = ""
        text2 = "新内容"
        
        diff = DiffUtils.calculate_text_diff(text1, text2)
        assert diff["total_changes"] > 0  # 有差异
        assert diff["similarity_ratio"] < 1.0

    def test_calculate_text_diff_complex(self):
        """测试复杂差异"""
        text1 = """第一行
第二行
第三行"""
        text2 = """第一行
修改的第二行
第三行
新增行"""
        
        diff = DiffUtils.calculate_text_diff(text1, text2)
        assert diff["total_changes"] > 0
        assert diff["similarity_ratio"] < 1.0

    def test_calculate_text_diff_unicode(self):
        """测试Unicode文本差异"""
        text1 = "测试内容：你好世界"
        text2 = "修改内容：你好世界🌍"
        
        diff = DiffUtils.calculate_text_diff(text1, text2)
        assert isinstance(diff, dict)
        assert "total_changes" in diff
        assert "similarity_ratio" in diff


class TestConfigurationAndEnvironment:
    """配置和环境测试"""

    def test_config_loading(self):
        """测试配置加载"""
        from app.core.config import settings
        
        assert hasattr(settings, 'APP_NAME')
        assert hasattr(settings, 'DEBUG')
        assert hasattr(settings, 'DATABASE_URL')

    def test_database_connection(self):
        """测试数据库连接"""
        from app.core.database import get_db, engine
        
        # 测试引擎创建
        assert engine is not None
        
        # 测试数据库生成器
        db_gen = get_db()
        assert db_gen is not None

    def test_metrics_collection(self):
        """测试指标收集"""
        from app.core.metrics import metrics_collector
        
        # 测试指标收集器初始化
        assert metrics_collector is not None
        
        # 测试指标记录
        metrics_collector.record_api_call("/test", "GET", 200, 0.1)
        metrics_collector.record_business_metric("test_metric", 1)

    def test_middleware_initialization(self):
        """测试中间件初始化"""
        from app.middleware.metrics_middleware import MetricsMiddleware
        
        # 测试中间件创建
        from app.main import app
        middleware_instances = [m for m in app.user_middleware if isinstance(m.cls, type) and issubclass(m.cls, MetricsMiddleware)]
        assert len(middleware_instances) > 0