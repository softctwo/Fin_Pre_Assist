"""功能测试脚本 - 端到端测试"""
import requests
import json
import time
from typing import Dict


class E2ETestRunner:
    """端到端测试运行器"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.api_prefix = "/api/v1"
        self.token = None
        self.headers = {}

    def run_all_tests(self):
        """运行所有测试"""
        print("=" * 60)
        print("开始端到端功能测试")
        print("=" * 60)

        try:
            # 1. 健康检查
            self.test_health_check()

            # 2. 用户注册和登录
            self.test_user_registration()
            self.test_user_login()

            # 3. 文档管理测试
            self.test_document_upload()
            self.test_document_list()

            # 4. 知识库测试
            self.test_knowledge_creation()
            self.test_knowledge_search()

            # 5. 模板测试
            self.test_template_creation()
            self.test_template_preview()

            # 6. 方案生成测试
            self.test_proposal_creation()

            # 7. 搜索测试
            self.test_semantic_search()

            print("\n" + "=" * 60)
            print("✅ 所有测试通过！")
            print("=" * 60)

        except Exception as e:
            print(f"\n❌ 测试失败: {e}")
            raise

    def test_health_check(self):
        """测试健康检查"""
        print("\n[TEST] 健康检查...")
        response = requests.get(f"{self.base_url}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print("✓ 健康检查通过")

    def test_user_registration(self):
        """测试用户注册"""
        print("\n[TEST] 用户注册...")
        response = requests.post(
            f"{self.base_url}{self.api_prefix}/auth/register",
            json={
                "username": f"testuser_{int(time.time())}",
                "email": f"test_{int(time.time())}@example.com",
                "password": "testpass123"
            }
        )
        assert response.status_code == 201
        print("✓ 用户注册成功")

    def test_user_login(self):
        """测试用户登录"""
        print("\n[TEST] 用户登录...")

        # 先注册一个用户
        username = f"logintest_{int(time.time())}"
        password = "testpass123"

        requests.post(
            f"{self.base_url}{self.api_prefix}/auth/register",
            json={
                "username": username,
                "email": f"{username}@example.com",
                "password": password
            }
        )

        # 登录
        response = requests.post(
            f"{self.base_url}{self.api_prefix}/auth/login",
            data={"username": username, "password": password}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data

        # 保存token
        self.token = data["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
        print("✓ 用户登录成功")

    def test_document_upload(self):
        """测试文档上传"""
        print("\n[TEST] 文档上传...")

        # 创建测试文件
        files = {
            'file': ('test.txt', b'This is a test document content', 'text/plain')
        }
        data = {
            'title': '测试文档',
            'doc_type': 'technical_proposal',
            'industry': '金融'
        }

        response = requests.post(
            f"{self.base_url}{self.api_prefix}/documents/upload",
            files=files,
            data=data,
            headers=self.headers
        )
        assert response.status_code == 201
        print("✓ 文档上传成功")

    def test_document_list(self):
        """测试文档列表"""
        print("\n[TEST] 获取文档列表...")
        response = requests.get(
            f"{self.base_url}{self.api_prefix}/documents/",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "items" in data
        print(f"✓ 获取到 {data['total']} 个文档")

    def test_knowledge_creation(self):
        """测试知识库创建"""
        print("\n[TEST] 创建知识库...")
        response = requests.post(
            f"{self.base_url}{self.api_prefix}/knowledge/",
            json={
                "category": "产品介绍",
                "title": "核心银行系统",
                "content": "核心银行系统是金融机构的核心业务处理系统，提供账户管理、交易处理等功能。",
                "tags": ["银行", "核心系统"]
            },
            headers=self.headers
        )
        assert response.status_code == 201
        print("✓ 知识库创建成功")

    def test_knowledge_search(self):
        """测试知识库搜索"""
        print("\n[TEST] 知识库搜索...")
        response = requests.post(
            f"{self.base_url}{self.api_prefix}/knowledge/search",
            params={"query": "银行系统", "limit": 5},
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        print(f"✓ 搜索到 {data.get('total', 0)} 条知识")

    def test_template_creation(self):
        """测试模板创建"""
        print("\n[TEST] 创建模板...")
        response = requests.post(
            f"{self.base_url}{self.api_prefix}/templates/",
            json={
                "name": "测试方案模板",
                "type": "proposal",
                "description": "用于测试的方案模板",
                "content": """
# {{ customer_name }} 项目方案

## 客户需求
{{ requirements }}

## 解决方案
{{ solution_overview }}
"""
            },
            headers=self.headers
        )
        assert response.status_code == 201
        template_id = response.json()["id"]
        print(f"✓ 模板创建成功 (ID: {template_id})")
        return template_id

    def test_template_preview(self):
        """测试模板预览"""
        print("\n[TEST] 模板预览...")

        # 先创建模板
        template_id = self.test_template_creation()

        # 预览模板
        response = requests.post(
            f"{self.base_url}{self.api_prefix}/templates/{template_id}/preview",
            json={
                "customer_name": "测试银行",
                "requirements": "系统升级",
                "solution_overview": "微服务架构"
            },
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "preview" in data
        print("✓ 模板预览成功")

    def test_proposal_creation(self):
        """测试方案创建"""
        print("\n[TEST] 创建方案...")
        response = requests.post(
            f"{self.base_url}{self.api_prefix}/proposals/",
            json={
                "title": "测试银行核心系统升级方案",
                "customer_name": "测试银行",
                "customer_industry": "金融",
                "requirements": """
需要升级现有核心银行系统，实现以下目标：
1. 提升系统性能和处理能力
2. 支持更多业务场景
3. 提高系统可靠性和安全性
"""
            },
            headers=self.headers
        )
        assert response.status_code == 201
        proposal_id = response.json()["id"]
        print(f"✓ 方案创建成功 (ID: {proposal_id})")
        return proposal_id

    def test_semantic_search(self):
        """测试语义搜索"""
        print("\n[TEST] 语义搜索...")
        response = requests.post(
            f"{self.base_url}{self.api_prefix}/search/documents",
            params={"query": "银行核心系统", "limit": 5},
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        print(f"✓ 语义搜索完成，找到 {data.get('total', 0)} 条结果")


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("金融售前方案辅助系统 - 功能测试")
    print("=" * 60)
    print("\n请确保后端服务已启动: http://localhost:8000")
    input("按Enter键开始测试...")

    runner = E2ETestRunner()
    runner.run_all_tests()


if __name__ == "__main__":
    main()
