"""API集成测试"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import get_db
from app.models.base import Base
from app.models import User, UserRole
from app.api.auth import get_password_hash


# 创建测试数据库
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """覆盖数据库依赖"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client():
    """创建测试客户端"""
    Base.metadata.create_all(bind=engine)
    yield TestClient(app)
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user(client):
    """创建测试用户"""
    db = TestingSessionLocal()
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash=get_password_hash("testpass123"),
        role=UserRole.USER,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    return user


@pytest.fixture
def auth_headers(client, test_user):
    """获取认证头"""
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "testuser", "password": "testpass123"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


class TestAuthAPI:
    """测试认证API"""

    def test_register(self, client):
        """测试用户注册"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "newuser",
                "email": "new@example.com",
                "password": "password123"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "newuser"
        assert data["email"] == "new@example.com"

    def test_login(self, client, test_user):
        """测试用户登录"""
        response = client.post(
            "/api/v1/auth/login",
            data={"username": "testuser", "password": "testpass123"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_get_current_user(self, client, auth_headers):
        """测试获取当前用户"""
        response = client.get("/api/v1/auth/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"


class TestTemplateAPI:
    """测试模板API"""

    def test_create_template(self, client, auth_headers):
        """测试创建模板"""
        response = client.post(
            "/api/v1/templates/",
            json={
                "name": "测试模板",
                "type": "proposal",
                "description": "测试用模板",
                "content": "客户: {{ customer_name }}"
            },
            headers=auth_headers
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "测试模板"

    def test_list_templates(self, client, auth_headers):
        """测试列出模板"""
        response = client.get("/api/v1/templates/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "items" in data

    def test_validate_template(self, client, auth_headers):
        """测试验证模板"""
        response = client.post(
            "/api/v1/templates/validate",
            json={"content": "Hello {{ name }}"},
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True


class TestKnowledgeAPI:
    """测试知识库API"""

    def test_create_knowledge(self, client, auth_headers):
        """测试创建知识"""
        response = client.post(
            "/api/v1/knowledge/",
            json={
                "category": "产品介绍",
                "title": "测试产品",
                "content": "这是测试产品的详细介绍",
                "tags": ["测试", "产品"]
            },
            headers=auth_headers
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "测试产品"

    def test_list_knowledge(self, client, auth_headers):
        """测试列出知识"""
        response = client.get("/api/v1/knowledge/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "items" in data

    def test_get_categories(self, client, auth_headers):
        """测试获取分类"""
        response = client.get("/api/v1/knowledge/categories", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "categories" in data


class TestProposalAPI:
    """测试方案API"""

    def test_create_proposal(self, client, auth_headers):
        """测试创建方案"""
        response = client.post(
            "/api/v1/proposals/",
            json={
                "title": "测试方案",
                "customer_name": "测试客户",
                "customer_industry": "金融",
                "requirements": "需要开发一个系统"
            },
            headers=auth_headers
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "测试方案"
        assert data["status"] == "draft"

    def test_list_proposals(self, client, auth_headers):
        """测试列出方案"""
        response = client.get("/api/v1/proposals/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "items" in data


class TestSearchAPI:
    """测试搜索API"""

    def test_search_stats(self, client, auth_headers):
        """测试获取搜索统计"""
        response = client.get("/api/v1/search/stats", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "collections" in data


class TestHealthCheck:
    """测试健康检查"""

    def test_health_check(self, client):
        """测试健康检查端点"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_root_endpoint(self, client):
        """测试根端点"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
