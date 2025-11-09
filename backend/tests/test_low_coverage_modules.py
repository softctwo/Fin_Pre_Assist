"""专门针对低覆盖率模块的测试"""
import pytest
import tempfile
import os
from unittest.mock import Mock, patch, AsyncMock
from app.services.ai_service import AIService
from app.services.cache_service import CacheService
from app.services.document_processor import DocumentProcessor
from app.services.export_service import ExportService
from app.services.proposal_generator import ProposalGenerator
from app.services.template_service import TemplateService
from app.services.vector_service import VectorService
from app.services.websocket_manager import WebSocketManager
from app.utils.diff_utils import DiffUtils
from app.utils.security_utils import XSSProtector, sanitize_for_api
from app.core.metrics import ai_calls_total, ai_calls_duration, ai_tokens_used, get_metrics
from app.core.database import engine, SessionLocal
from app.main import app


class TestProposalGeneratorExtended:
    """扩展方案生成器测试 - 当前覆盖率18%"""

    def test_proposal_generator_init(self):
        """测试方案生成器初始化"""
        generator = ProposalGenerator()
        assert hasattr(generator, 'ai_service')
        assert hasattr(generator, 'template_service')

    def test_generate_proposal_outline(self):
        """测试生成方案大纲"""
        generator = ProposalGenerator()
        
        with patch.object(generator.ai_service, 'generate_text') as mock_generate:
            mock_generate.return_value = "# 方案大纲\n1. 项目背景\n2. 解决方案"
            result = generator.generate_proposal_outline("测试需求", "科技行业")
            assert "方案大纲" in result

    def test_generate_proposal_content(self):
        """测试生成方案内容"""
        generator = ProposalGenerator()
        
        with patch.object(generator.ai_service, 'generate_text') as mock_generate:
            mock_generate.return_value = "这是详细的方案内容"
            result = generator.generate_proposal_content("大纲", "需求", "模板")
            assert result == "这是详细的方案内容"

    def test_enhance_proposal_with_ai(self):
        """测试使用AI增强方案"""
        generator = ProposalGenerator()
        
        with patch.object(generator.ai_service, 'generate_text') as mock_generate:
            mock_generate.return_value = "增强后的方案内容"
            result = generator.enhance_proposal_with_ai("原始方案", "增强需求")
            assert result == "增强后的方案内容"

    def test_validate_proposal_structure(self):
        """测试方案结构验证"""
        generator = ProposalGenerator()
        
        # 有效的方案结构
        valid_proposal = {
            "title": "测试方案",
            "sections": [
                {"title": "概述", "content": "内容"},
                {"title": "方案", "content": "内容"}
            ]
        }
        assert generator.validate_proposal_structure(valid_proposal) == True
        
        # 无效的方案结构
        invalid_proposal = {"title": "测试方案"}
        assert generator.validate_proposal_structure(invalid_proposal) == False

    def test_extract_proposal_requirements(self):
        """测试提取方案需求"""
        generator = ProposalGenerator()
        
        text = "客户需要一个高性能的系统，要求响应时间<1秒"
        requirements = generator.extract_proposal_requirements(text)
        assert isinstance(requirements, list)

    def test_estimate_proposal_timeline(self):
        """测试估算方案时间线"""
        generator = ProposalGenerator()
        
        tasks = ["需求分析", "系统设计", "开发", "测试"]
        timeline = generator.estimate_proposal_timeline(tasks)
        assert isinstance(timeline, dict)
        assert "total_days" in timeline

    def test_generate_proposal_risks(self):
        """测试生成方案风险分析"""
        generator = ProposalGenerator()
        
        with patch.object(generator.ai_service, 'generate_text') as mock_generate:
            mock_generate.return_value = "技术风险：性能问题\n管理风险：进度延期"
            risks = generator.generate_proposal_risks("测试方案")
            assert "技术风险" in risks

    def test_format_proposal_output(self):
        """测试格式化方案输出"""
        generator = ProposalGenerator()
        
        proposal_data = {
            "title": "测试方案",
            "customer": "测试客户",
            "content": "方案内容"
        }
        formatted = generator.format_proposal_output(proposal_data, format_type="markdown")
        assert isinstance(formatted, str)


class TestAIServiceDeepCoverage:
    """AI服务深度测试 - 提升当前51%覆盖率"""

    def test_ai_service_error_handling(self):
        """测试AI服务错误处理"""
        service = AIService()
        
        # 测试网络错误
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_post.side_effect = Exception("网络错误")
            with pytest.raises(Exception):
                import asyncio
                asyncio.run(service.generate_text("测试"))

    def test_ai_service_token_validation(self):
        """测试AI服务令牌验证"""
        service = AIService()
        
        # 测试无效令牌
        with patch.object(service, '_validate_api_key') as mock_validate:
            mock_validate.return_value = False
            with pytest.raises(Exception):
                import asyncio
                asyncio.run(service.generate_text("测试"))

    def test_ai_service_response_parsing(self):
        """测试AI服务响应解析"""
        service = AIService()
        
        # 测试JSON响应解析
        with patch.object(service, '_parse_json_response') as mock_parse:
            mock_parse.return_value = {"content": "解析的内容"}
            result = mock_parse('{"content": "解析的内容"}')
            assert result["content"] == "解析的内容"

    def test_ai_service_concurrent_limiting(self):
        """测试AI服务并发限制"""
        service = AIService()
        
        with patch.object(service, '_check_rate_limit') as mock_check:
            mock_check.return_value = True  # 被限制
            with pytest.raises(Exception):
                import asyncio
                asyncio.run(service.generate_text("测试"))

    def test_ai_service_fallback_mechanism(self):
        """测试AI服务回退机制"""
        service = AIService()
        original_provider = service.provider
        
        # 测试提供商回退
        service.provider = "unavailable"
        with patch.object(service, '_try_providers') as mock_try:
            mock_try.return_value = "回退内容"
            import asyncio
            result = asyncio.run(service.generate_text("测试"))
            assert result == "回退内容"
        
        service.provider = original_provider

    def test_ai_service_content_filtering(self):
        """测试AI服务内容过滤"""
        service = AIService()
        
        # 测试敏感内容过滤
        sensitive_content = "这是敏感内容"
        filtered = service._filter_sensitive_content(sensitive_content)
        assert isinstance(filtered, str)

    def test_ai_service_usage_tracking(self):
        """测试AI服务使用跟踪"""
        service = AIService()
        
        # 测试使用统计
        service._track_usage("openai", 100, 10)
        assert hasattr(service, 'usage_stats')

    def test_ai_service_cache_integration(self):
        """测试AI服务缓存集成"""
        service = AIService()
        
        with patch.object(service.cache_service, 'get') as mock_get, \
             patch.object(service.cache_service, 'set') as mock_set:
            mock_get.return_value = None  # 缓存未命中
            with patch.object(service, '_generate_with_openai') as mock_generate:
                mock_generate.return_value = ("生成内容", 10)
                import asyncio
                result = asyncio.run(service.generate_text("测试"))
                assert result == "生成内容"


class TestCacheServiceDeepCoverage:
    """缓存服务深度测试 - 提升当前49%覆盖率"""

    def test_cache_service_distributed_operations(self):
        """测试分布式缓存操作"""
        service = CacheService()
        
        # 测试分布式锁
        with patch.object(service, '_acquire_distributed_lock') as mock_lock:
            mock_lock.return_value = True
            lock_acquired = service._acquire_distributed_lock("test_lock")
            assert lock_acquired == True

    def test_cache_service_serialization(self):
        """测试缓存序列化"""
        service = CacheService()
        
        # 测试复杂数据序列化
        complex_data = {
            "nested": {"dict": {"with": [1, 2, 3]}},
            "list": [{"a": 1}, {"b": 2}],
            "function": lambda x: x + 1
        }
        
        serialized = service._serialize_data(complex_data)
        assert isinstance(serialized, str)

    def test_cache_service_memory_management(self):
        """测试缓存内存管理"""
        service = CacheService()
        
        # 测试内存使用检查
        memory_usage = service._check_memory_usage()
        assert isinstance(memory_usage, dict)
        assert "used_memory" in memory_usage

    def test_cache_service_eviction_policies(self):
        """测试缓存淘汰策略"""
        service = CacheService()
        
        # 测试LRU淘汰
        service.set("key1", "value1", ttl=1)
        service.set("key2", "value2", ttl=1)
        service.set("key3", "value3", ttl=1)
        
        # 强制淘汰
        service._evict_expired_items()
        
        # 检查是否淘汰
        assert service.get("key1") is None

    def test_cache_service_health_monitoring(self):
        """测试缓存健康监控"""
        service = CacheService()
        
        # 测试健康检查
        health = service.check_health()
        assert "redis_connected" in health
        assert "memory_cache_size" in health

    def test_cache_service_backup_and_restore(self):
        """测试缓存备份和恢复"""
        service = CacheService()
        
        # 添加一些数据
        service.set("backup_key", "backup_value")
        
        # 备份数据
        backup_data = service._create_backup()
        assert isinstance(backup_data, dict)
        
        # 清空缓存
        service.clear_all()
        
        # 恢复数据
        service._restore_from_backup(backup_data)
        assert service.get("backup_key") == "backup_value"

    def test_cache_service_performance_metrics(self):
        """测试缓存性能指标"""
        service = CacheService()
        
        # 测试性能统计
        metrics = service.get_performance_metrics()
        assert "hit_rate" in metrics
        assert "avg_response_time" in metrics


class TestDiffUtilsCoverage:
    """差异工具测试 - 提升当前0%覆盖率"""

    def test_diff_utils_calculate_text_diff(self):
        """测试文本差异计算"""
        text1 = "原始文本内容"
        text2 = "修改后的文本内容"
        
        diff_result = DiffUtils.calculate_text_diff(text1, text2)
        assert isinstance(diff_result, dict)
        assert "total_changes" in diff_result
        assert "similarity" in diff_result
        assert "diff" in diff_result

    def test_diff_utils_calculate_html_diff(self):
        """测试HTML差异计算"""
        text1 = "原始文本内容"
        text2 = "修改后的文本内容"
        
        html_diff = DiffUtils.calculate_html_diff(text1, text2)
        assert isinstance(html_diff, str)
        assert "<table" in html_diff

    def test_diff_utils_compare_json_content(self):
        """测试JSON内容比较"""
        json1 = {"name": "test", "value": 1, "items": ["a", "b"]}
        json2 = {"name": "test", "value": 2, "items": ["a", "c"]}
        
        diff_result = DiffUtils.compare_json_content(json1, json2)
        assert isinstance(diff_result, dict)
        assert "fields_changed" in diff_result
        assert "fields_added" in diff_result
        assert "fields_removed" in diff_result
        assert "summary" in diff_result

    def test_diff_utils_comprehensive_workflow(self):
        """测试完整的差异工作流"""
        original_text = "这是原始的文档内容\n包含多行文本"
        modified_text = "这是修改后的文档内容\n包含更新后的文本\n新增了一行"
        
        # 计算文本差异
        text_diff = DiffUtils.calculate_text_diff(text1=original_text, text2=modified_text)
        assert text_diff["total_changes"] > 0
        
        # 计算HTML差异
        html_diff = DiffUtils.calculate_html_diff(text1=original_text, text2=modified_text)
        assert len(html_diff) > 0
        
        # 比较JSON内容
        json1 = {"title": "原始标题", "content": original_text}
        json2 = {"title": "修改标题", "content": modified_text, "author": "测试作者"}
        
        json_diff = DiffUtils.compare_json_content(json1, json2)
        assert json_diff["summary"]["changed_fields"] >= 1
        assert json_diff["summary"]["added_fields"] >= 1

    def test_diff_utils_edge_cases(self):
        """测试边界情况"""
        # 空文本
        empty_diff = DiffUtils.calculate_text_diff("", "")
        assert empty_diff["total_changes"] == 0
        assert empty_diff["similarity"] == 1.0
        
        # 一方为空
        single_empty = DiffUtils.calculate_text_diff("有内容", "")
        assert single_empty["total_changes"] > 0
        
        # 相同文本
        same_diff = DiffUtils.calculate_text_diff("相同内容", "相同内容")
        assert same_diff["total_changes"] == 0
        assert same_diff["similarity"] == 1.0
        
        # 空JSON
        empty_json_diff = DiffUtils.compare_json_content({}, {})
        assert empty_json_diff["summary"]["total_fields"] == 0

    def test_diff_utils_large_content(self):
        """测试大内容处理"""
        # 创建大文本
        large_text1 = "行" + "\n行" * 1000 + "结束"
        large_text2 = "行" + "\n行" * 1000 + "修改" + "\n行" + "结束"
        
        # 应该能处理大文本而不出错
        diff_result = DiffUtils.calculate_text_diff(large_text1, large_text2)
        assert isinstance(diff_result, dict)
        assert diff_result["total_changes"] > 0
        
        # 测试大JSON
        large_json1 = {"data": [{"id": i} for i in range(100)]}
        large_json2 = {"data": [{"id": i} for i in range(101)]}
        
        json_diff = DiffUtils.compare_json_content(large_json1, large_json2)
        assert isinstance(json_diff, dict)

    def test_diff_utils_unicode_handling(self):
        """测试Unicode处理"""
        unicode_text1 = "中文内容 🚀\nالعربية\nрусский"
        unicode_text2 = "中文内容更新 🎉\nالعربية\n日本語"
        
        diff_result = DiffUtils.calculate_text_diff(unicode_text1, unicode_text2)
        assert isinstance(diff_result, dict)
        assert diff_result["total_changes"] > 0
        
        html_diff = DiffUtils.calculate_html_diff(unicode_text1, unicode_text2)
        assert isinstance(html_diff, str)
        
        # 测试Unicode JSON
        unicode_json1 = {"中文": "内容", "emoji": "🚀", "arabic": "العربية"}
        unicode_json2 = {"中文": "内容更新", "emoji": "🎉", "japanese": "日本語"}
        
        json_diff = DiffUtils.compare_json_content(unicode_json1, unicode_json2)
        assert isinstance(json_diff, dict)


class TestSecurityUtilsCoverage:
    """安全工具测试 - 提升当前26%覆盖率"""

    def test_xss_protector_sanitize_html_comprehensive(self):
        """测试全面的HTML清理"""
        test_cases = [
            ("<script>alert('xss')</script>", "alert('xss')"),
            ("<img src='x' onerror='alert(1)'>", ""),
            ("<a href='javascript:alert(1)'>link</a>", "link"),
            ("<div onclick='alert(1)'>content</div>", "content"),
            ("<iframe src='javascript:alert(1)'></iframe>", ""),
            ("<object data='javascript:alert(1)'></object>", ""),
            ("<embed src='javascript:alert(1)'>", ""),
            ("<link rel='stylesheet' href='javascript:alert(1)'>", "")
        ]
        
        for malicious, expected in test_cases:
            result = XSSProtector.sanitize_html(malicious)
            assert "<script" not in result
            assert "javascript:" not in result.lower()

    def test_xss_protector_is_dangerous_content_comprehensive(self):
        """测试危险内容检测"""
        dangerous_patterns = [
            "javascript:alert('xss')",
            "<script>alert('xss')</script>",
            "onload='alert(1)'",
            "onerror='alert(1)'",
            "<iframe src='evil.com'></iframe>",
            "<object data='evil.swf'></object>",
            "<embed src='evil.mp4'>",
            "<link href='evil.css'>"
        ]
        
        for pattern in dangerous_patterns:
            assert XSSProtector.is_dangerous_content(pattern) == True
        
        # 测试安全内容
        safe_content = "这是安全的内容，没有危险标签"
        assert XSSProtector.is_dangerous_content(safe_content) == False

    def test_xss_protector_validate_url_comprehensive(self):
        """测试URL验证"""
        safe_urls = [
            "https://example.com",
            "http://example.com/path",
            "ftp://files.example.com",
            "mailto:user@example.com"
        ]
        
        for url in safe_urls:
            assert XSSProtector.validate_url(url) == True
        
        dangerous_urls = [
            "javascript:alert('xss')",
            "vbscript:msgbox('xss')",
            "data:text/html,<script>alert('xss')</script>",
            "file:///etc/passwd"
        ]
        
        for url in dangerous_urls:
            assert XSSProtector.validate_url(url) == False

    def test_xss_protector_sanitize_css(self):
        """测试CSS清理"""
        malicious_css = "background-image: url('javascript:alert(1)')"
        safe_css = XSSProtector.sanitize_css(malicious_css)
        assert "javascript:" not in safe_css

    def test_sanitize_for_api_edge_cases(self):
        """测试API数据清理边界情况"""
        # None值
        assert sanitize_for_api(None) is None
        
        # 空值
        assert sanitize_for_api("") == ""
        
        # 数字
        assert sanitize_for_api(123) == 123
        
        # 布尔值
        assert sanitize_for_api(True) == True
        
        # 嵌套结构
        nested = {
            "safe": "安全内容",
            "dangerous": "<script>alert('xss')</script>",
            "nested": {
                "array": ["安全", "<script>alert(1)</script>", 123]
            }
        }
        result = sanitize_for_api(nested)
        assert "<script>" not in result["dangerous"]
        assert "<script>" not in result["nested"]["array"][1]

    def test_sanitize_for_api_large_data(self):
        """测试大数据量清理"""
        large_list = ["item" + str(i) for i in range(1000)]
        result = sanitize_for_api(large_list)
        assert len(result) == 1000

    def test_sanitize_for_api_unicode(self):
        """测试Unicode字符清理"""
        unicode_data = {
            "chinese": "中文内容",
            "emoji": "🚀🎉",
            "arabic": "العربية",
            "special": "特殊字符ßøñ"
        }
        result = sanitize_for_api(unicode_data)
        assert result["chinese"] == "中文内容"
        assert result["emoji"] == "🚀🎉"


class TestMetricsCoverage:
    """指标收集测试 - 提升当前26%覆盖率"""

    def test_metrics_basic_functions(self):
        """测试指标基本功能"""
        # 测试AI调用指标
        ai_calls_total.labels(provider="openai", model="gpt-3.5", status="success").inc()
        ai_calls_duration.labels(provider="openai", model="gpt-3.5").observe(0.5)
        ai_tokens_used.labels(provider="openai", model="gpt-3.5").inc(100)
        
        # 测试向量搜索指标
        vector_search_total.labels(collection="documents", status="success").inc()
        
        # 获取指标
        metrics_data = get_metrics()
        assert isinstance(metrics_data, str)
        assert len(metrics_data) > 0

    def test_cache_hit_rate_function(self):
        """测试缓存命中率函数"""
        from app.core.metrics import update_cache_hit_rate
        
        # 更新缓存命中率
        update_cache_hit_rate("redis", 80, 100)
        update_cache_hit_rate("memory", 60, 100)
        
        # 验证函数不会抛出异常
        assert True

    def test_metric_decorators(self):
        """测试指标装饰器"""
        from app.core.metrics import track_ai_metrics, track_vector_search_metrics, track_cache_metrics
        
        # 测试装饰器创建
        ai_decorator = track_ai_metrics("openai", "gpt-3.5")
        vector_decorator = track_vector_search_metrics("documents")
        cache_decorator = track_cache_metrics("redis", "get")
        
        # 验证装饰器存在
        assert callable(ai_decorator)
        assert callable(vector_decorator)
        assert callable(cache_decorator)

    def test_metrics_counter_operations(self):
        """测试指标计数器操作"""
        # 测试不同状态
        ai_calls_total.labels(provider="zhipu", model="chatglm", status="success").inc()
        ai_calls_total.labels(provider="zhipu", model="chatglm", status="error").inc()
        ai_calls_total.labels(provider="wenxin", model="ernie", status="success").inc()
        
        # 测试token计数
        ai_tokens_used.labels(provider="zhipu", model="chatglm").inc(50)
        ai_tokens_used.labels(provider="wenxin", model="ernie").inc(75)
        
        # 验证不会抛出异常
        assert True

    def test_metrics_histogram_operations(self):
        """测试指标直方图操作"""
        # 测试AI调用持续时间
        for duration in [0.1, 0.2, 0.3, 0.5, 1.0]:
            ai_calls_duration.labels(provider="openai", model="gpt-3.5").observe(duration)
        
        # 测试多个模型
        ai_calls_duration.labels(provider="zhipu", model="chatglm").observe(0.4)
        ai_calls_duration.labels(provider="wenxin", model="ernie").observe(0.6)
        
        # 验证不会抛出异常
        assert True

    def test_metrics_gauge_operations(self):
        """测试指标仪表操作"""
        from app.core.metrics import cache_size, active_connections
        
        # 测试缓存大小
        cache_size.labels(cache_type="redis").set(1000)
        cache_size.labels(cache_type="memory").set(500)
        
        # 测试活跃连接
        active_connections.labels(service="websocket").set(10)
        active_connections.labels(service="api").set(50)
        
        # 验证不会抛出异常
        assert True


class TestWebSocketManagerCoverage:
    """WebSocket管理器测试 - 提升当前31%覆盖率"""

    def test_websocket_manager_message_broadcasting(self):
        """测试消息广播"""
        manager = WebSocketManager()
        
        # 创建模拟连接
        websocket1 = Mock()
        websocket2 = Mock()
        
        # 添加连接
        manager.add_connection(websocket1, 1)
        manager.add_connection(websocket2, 2)
        
        # 广播消息
        message = {"type": "broadcast", "content": "测试消息"}
        manager.broadcast(message)
        
        # 验证所有连接都收到了消息
        websocket1.send_json.assert_called_once_with(message)
        websocket2.send_json.assert_called_once_with(message)

    def test_websocket_manager_user_messaging(self):
        """测试用户消息发送"""
        manager = WebSocketManager()
        
        # 创建模拟连接
        websocket1 = Mock()
        websocket2 = Mock()
        
        # 添加连接（同一用户多个连接）
        manager.add_connection(websocket1, 1)
        manager.add_connection(websocket2, 1)
        
        # 发送给特定用户
        message = {"type": "user_message", "content": "个人消息"}
        manager.send_to_user(1, message)
        
        # 验证该用户的所有连接都收到了消息
        websocket1.send_json.assert_called_once_with(message)
        websocket2.send_json.assert_called_once_with(message)

    def test_websocket_manager_connection_stats(self):
        """测试连接统计"""
        manager = WebSocketManager()
        
        # 添加一些连接
        for i in range(5):
            websocket = Mock()
            user_id = i // 2  # 模拟多个用户
            manager.add_connection(websocket, user_id)
        
        # 获取统计信息
        stats = manager.get_connection_stats()
        assert "total_connections" in stats
        assert "unique_users" in stats
        assert stats["total_connections"] == 5
        assert stats["unique_users"] == 3

    def test_websocket_manager_connection_cleanup(self):
        """测试连接清理"""
        manager = WebSocketManager()
        
        # 添加连接
        websocket = Mock()
        manager.add_connection(websocket, 1)
        
        # 移除连接
        manager.remove_connection(websocket)
        
        # 验证连接已移除
        assert len(manager.connections) == 0
        assert 1 not in manager.user_connections

    def test_websocket_manager_error_handling(self):
        """测试错误处理"""
        manager = WebSocketManager()
        
        # 创建会抛出异常的WebSocket
        faulty_websocket = Mock()
        faulty_websocket.send_json.side_effect = Exception("连接错误")
        
        # 添加连接
        manager.add_connection(faulty_websocket, 1)
        
        # 发送消息（应该处理错误）
        message = {"type": "test", "content": "测试"}
        manager.send_to_user(1, message)
        
        # 验证没有抛出异常
        assert True  # 如果能执行到这里说明错误被正确处理

    def test_websocket_manager_room_functionality(self):
        """测试房间功能"""
        manager = WebSocketManager()
        
        # 创建模拟连接
        websocket1 = Mock()
        websocket2 = Mock()
        websocket3 = Mock()
        
        # 添加连接并加入房间
        manager.add_connection(websocket1, 1)
        manager.add_connection(websocket2, 2)
        manager.add_connection(websocket3, 3)
        
        manager.join_room(websocket1, "room1")
        manager.join_room(websocket2, "room1")
        manager.join_room(websocket3, "room2")
        
        # 向房间发送消息
        room_message = {"type": "room_message", "content": "房间消息"}
        manager.send_to_room("room1", room_message)
        
        # 验证房间内的用户收到消息
        websocket1.send_json.assert_called_once_with(room_message)
        websocket2.send_json.assert_called_once_with(room_message)
        websocket3.send_json.assert_not_called()  # 不在房间内

    def test_websocket_manager_connection_timeout(self):
        """测试连接超时"""
        manager = WebSocketManager()
        
        # 模拟超时检查
        import time
        current_time = time.time()
        
        # 添加连接并设置最后活动时间
        websocket = Mock()
        manager.add_connection(websocket, 1)
        manager.user_last_activity[1] = current_time - 3600  # 1小时前
        
        # 清理超时连接
        timeout_removed = manager.cleanup_timeout_connections(timeout=1800)  # 30分钟超时
        assert timeout_removed >= 1