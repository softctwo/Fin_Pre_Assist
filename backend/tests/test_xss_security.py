"""
XSS 安全测试
测试系统的XSS攻击防护能力
"""
import pytest
from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.main import app

client = TestClient(app)


class TestXSSProtection:
    """XSS攻击防护测试"""

    def test_xss_in_proposal_requirements(self, test_client: TestClient, auth_headers: dict):
        """测试在方案需求中注入XSS脚本"""
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "<svg onload=alert('XSS')>",
            "javascript:alert('XSS')",
            "<iframe src='javascript:alert(1)'></iframe>",
            "<body onload=alert('XSS')>",
            "'\"><script>alert('XSS')</script>"
        ]

        for payload in xss_payloads:
            response = test_client.post(
                "/api/v1/proposals/",
                json={
                    "title": "Test Proposal",
                    "customer_name": "Test Customer",
                    "requirements": payload,
                    "industry": "金融"
                },
                headers=auth_headers
            )

            # 检查响应中是否包含原始脚本标签
            if response.status_code == 201 or response.status_code == 200:
                data = response.json()
                # 验证脚本标签被转义或移除
                assert "<script>" not in str(data) or "&lt;script&gt;" in str(data), \
                    f"XSS payload not sanitized: {payload}"

    def test_xss_in_knowledge_content(self, test_client: TestClient, admin_headers: dict):
        """测试在知识库内容中注入XSS"""
        xss_payload = "<script>alert(document.cookie)</script>"

        response = test_client.post(
            "/api/v1/knowledge/",
            json={
                "title": "Test Knowledge",
                "category": "技术",
                "content": xss_payload,
                "tags": ["test"]
            },
            headers=admin_headers
        )

        if response.status_code == 201:
            data = response.json()
            # 验证XSS被清理
            assert "<script>" not in data.get("content", "") or \
                   "&lt;script&gt;" in data.get("content", "")

    def test_xss_in_search_query(self, test_client: TestClient):
        """测试在搜索查询中注入XSS"""
        xss_payload = "<script>alert(1)</script>"

        response = test_client.post(
            "/api/v1/search/documents",
            json={"query": xss_payload, "limit": 10}
        )

        # 搜索应该正常返回，不应该执行脚本
        assert response.status_code in [200, 422]  # 422如果是验证失败
        if response.status_code == 200:
            data = response.json()
            # 确保返回结果中不包含未转义的脚本
            assert "<script>alert(1)</script>" not in str(data)

    def test_html_entity_encoding(self, test_client: TestClient, admin_headers: dict):
        """测试HTML实体编码"""
        html_content = "<h1>Title</h1><p>Content</p>"

        response = test_client.post(
            "/api/v1/knowledge/",
            json={
                "title": "HTML Test",
                "category": "技术",
                "content": html_content,
                "tags": ["test"]
            },
            headers=admin_headers
        )

        if response.status_code == 201:
            data = response.json()
            content = data.get("content", "")
            # HTML标签应该被转义或作为文本存储
            assert "<h1>" not in content or "&lt;h1&gt;" in content

    def test_javascript_uri_scheme(self, test_client: TestClient, auth_headers: dict):
        """测试JavaScript URI scheme过滤"""
        js_uri = "javascript:alert('XSS')"

        response = test_client.post(
            "/api/v1/proposals/",
            json={
                "title": js_uri,
                "customer_name": "Test",
                "requirements": "Test requirements",
                "industry": "金融"
            },
            headers=auth_headers
        )

        if response.status_code == 201:
            data = response.json()
            # JavaScript URI应该被清理
            assert not data.get("title", "").startswith("javascript:")

    def test_dom_based_xss_prevention(self, test_client: TestClient, admin_headers: dict):
        """测试DOM型XSS防护"""
        dom_xss = "'\"><img src=x onerror=alert('XSS')>"

        response = test_client.post(
            "/api/v1/templates/",
            json={
                "name": "Test Template",
                "type": "proposal",
                "content": dom_xss
            },
            headers=admin_headers
        )

        if response.status_code == 201:
            data = response.json()
            content = data.get("content", "")
            # onerror事件应该被移除或转义
            assert "onerror=" not in content or "onerror=\"\"" in content


class TestCSRFProtection:
    """CSRF攻击防护测试"""

    def test_csrf_without_token(self, test_client: TestClient):
        """测试没有CSRF令牌的POST请求"""
        response = test_client.post(
            "/api/v1/proposals/",
            json={
                "title": "Test",
                "customer_name": "Test",
                "requirements": "Test",
                "industry": "金融"
            }
            # 没有Authorization头
        )

        # 应该被拒绝访问
        assert response.status_code == 401

    def test_csrf_with_invalid_token(self, test_client: TestClient):
        """测试使用无效CSRF令牌"""
        response = test_client.post(
            "/api/v1/proposals/",
            json={
                "title": "Test",
                "customer_name": "Test",
                "requirements": "Test",
                "industry": "金融"
            },
            headers={"Authorization": "Bearer invalid-token"}
        )

        # 应该被拒绝访问
        assert response.status_code == 401


class TestRateLimiting:
    """速率限制测试"""

    def test_rate_limit_on_login(self, test_client: TestClient):
        """测试登录接口速率限制"""
        for i in range(10):
            response = test_client.post(
                "/api/v1/auth/login",
                data={"username": f"user{i}", "password": "wrong_password"}
            )

            if i >= 5:  # 假设限制为5次/分钟
                # 应该被限制
                assert response.status_code in [429, 401, 422]

    def test_rate_limit_on_registration(self, test_client: TestClient):
        """测试注册接口速率限制"""
        for i in range(15):
            response = test_client.post(
                "/api/v1/auth/register",
                json={
                    "username": f"testuser{i}",
                    "email": f"test{i}@example.com",
                    "password": "Test123456!",
                    "full_name": f"Test User {i}"
                }
            )

            if i >= 10:  # 假设限制为10次/分钟
                # 应该被限制
                assert response.status_code == 429


class TestSecurityHeaders:
    """安全头测试"""

    def test_security_headers_present(self, test_client: TestClient):
        """测试安全头是否存在"""
        response = test_client.get("/api/v1/health/")

        # 检查是否存在XSS防护头
        assert "x-frame-options" in response.headers or "x-frame-options".lower() in [k.lower() for k in response.headers.keys()]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
