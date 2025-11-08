"""
Locust 性能测试脚本
运行: locust -f tests/locustfile.py --host=http://localhost:8000
"""

from locust import HttpUser, task, between, events
from locust.runners import MasterRunner
import json


class FinPreAssistUser(HttpUser):
    """模拟标准用户行为"""
    wait_time = between(1, 3)

    def on_start(self):
        """用户启动时登录"""
        self.login()

    def login(self):
        """登录获取token"""
        response = self.client.post("/api/v1/auth/login", json={
            "username": "testuser",
            "password": "Test123456!"
        })

        if response.status_code == 200:
            self.token = response.json()["access_token"]
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            self.token = None
            self.headers = {}

    @task(3)
    def list_proposals(self):
        """获取方案列表"""
        self.client.get("/api/v1/proposals/", headers=self.headers)

    @task(2)
    def search_documents(self):
        """搜索文档"""
        self.client.post("/api/v1/search/documents", json={
            "query": "金融系统",
            "limit": 10
        }, headers=self.headers)

    @task(1)
    def search_knowledge(self):
        """搜索知识库"""
        self.client.post("/api/v1/search/knowledge", json={
            "query": "金融科技",
            "limit": 5,
            "category": "技术"
        }, headers=self.headers)

    @task(1)
    def get_health(self):
        """健康检查"""
        self.client.get("/api/v1/health/")


class ProposalHeavyUser(HttpUser):
    """重负载用户 - 频繁创建方案"""
    wait_time = between(0.5, 1.5)
    weight = 2

    def on_start(self):
        """用户启动时登录"""
        self.login()
        self.counter = 0

    def login(self):
        """登录获取token"""
        response = self.client.post("/api/v1/auth/login", json={
            "username": "testuser",
            "password": "Test123456!"
        })

        if response.status_code == 200:
            self.token = response.json()["access_token"]
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            self.token = None
            self.headers = {}

    @task(5)
    def create_proposal(self):
        """创建新方案"""
        self.counter += 1
        response = self.client.post("/api/v1/proposals/", json={
            "title": f"Performance Test Proposal {self.counter}",
            "customer_name": f"Customer {self.counter}",
            "requirements": "性能测试需求",
            "industry": "金融",
            "customer_industry": "银行",
            "budget_range": "100-500万"
        }, headers=self.headers)

        if response.status_code == 201:
            proposal_id = response.json()["id"]
            # 获取方案详情
            self.client.get(f"/api/v1/proposals/{proposal_id}", headers=self.headers)

    @task(2)
    def search_similar_proposals(self):
        """搜索相似方案"""
        self.client.post("/api/v1/search/proposals/similar", json={
            "requirements": "核心银行系统",
            "limit": 5
        }, headers=self.headers)

    @task(1)
    def get_proposal_list_filtered(self):
        """带过滤条件的方案列表"""
        self.client.get("/api/v1/proposals/?status=active&skip=0&limit=20", headers=self.headers)


class DocumentManagerUser(HttpUser):
    """文档管理用户"""
    wait_time = between(2, 4)

    def on_start(self):
        """用户启动时登录"""
        self.login()

    def login(self):
        """登录获取token"""
        response = self.client.post("/api/v1/auth/login", json={
            "username": "testuser",
            "password": "Test123456!"
        })

        if response.status_code == 200:
            self.token = response.json()["access_token"]
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            self.token = None
            self.headers = {}

    @task(3)
    def list_documents(self):
        """获取文档列表"""
        self.client.get("/api/v1/documents/", headers=self.headers)

    @task(1)
    def list_documents_filtered(self):
        """带过滤的文档列表"""
        self.client.get("/api/v1/documents/?document_type=proposal&skip=0&limit=10", headers=self.headers)

    @task(2)
    def search_documents(self):
        """搜索文档"""
        self.client.post("/api/v1/search/documents", json={
            "query": "银行核心系统",
            "limit": 10
        }, headers=self.headers)

    @task(1)
    def get_document_stats(self):
        """获取文档统计"""
        self.client.get("/api/v1/documents/stats", headers=self.headers)


# Test configuration
if __name__ == "__main__":
    import os
    os.system("locust -f locustfile.py --host=http://localhost:8000")
