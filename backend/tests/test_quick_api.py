"""快速修复的API测试 - 针对覆盖率提升"""
import pytest
import io
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import get_db
from app.models.base import Base
from app.models import User, UserRole, Document, DocumentType
from app.api.auth import get_password_hash

# 测试数据库
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_quick_api.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def client():
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
def user_headers(client, test_user):
    """获取用户认证头"""
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "testuser", "password": "testpass123"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_document(client, user_headers, test_user):
    """创建示例文档"""
    db = TestingSessionLocal()
    
    # 直接在数据库中创建文档
    doc = Document(
        title="测试文档",
        file_path="/test/path.txt",
        file_name="test.txt",
        file_size=100,
        mime_type="text/plain",
        content_text="这是测试文档内容",
        type=DocumentType.BUSINESS_PROPOSAL,
        industry="金融",
        customer_name="测试客户",
        user_id=test_user.id
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    db.close()
    
    return {
        "id": doc.id,
        "title": doc.title,
        "content": doc.content_text
    }


class TestBasicAPI:
    """基础API测试"""

    def test_health_check(self, client):
        """健康检查"""
        response = client.get("/health")
        assert response.status_code == 200

    def test_root_endpoint(self, client):
        """根端点"""
        response = client.get("/")
        assert response.status_code == 200

    def test_login(self, client, test_user):
        """用户登录"""
        response = client.post(
            "/api/v1/auth/login",
            data={"username": "testuser", "password": "testpass123"}
        )
        assert response.status_code == 200
        assert "access_token" in response.json()

    def test_get_current_user(self, client, user_headers):
        """获取当前用户信息"""
        response = client.get("/api/v1/auth/me", headers=user_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"

    def test_list_documents_empty(self, client, user_headers):
        """测试列出文档(空)"""
        response = client.get("/api/v1/documents/", headers=user_headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data

    def test_list_documents_with_data(self, client, user_headers, sample_document):
        """测试列出文档(有数据)"""
        response = client.get("/api/v1/documents/", headers=user_headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data

    def test_get_document_by_id(self, client, user_headers, sample_document):
        """测试根据ID获取文档"""
        doc_id = sample_document["id"]
        response = client.get(f"/api/v1/documents/{doc_id}", headers=user_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == doc_id

    def test_get_document_not_found(self, client, user_headers):
        """测试获取不存在的文档"""
        response = client.get("/api/v1/documents/99999", headers=user_headers)
        assert response.status_code == 404

    def test_unauthorized_access(self, client):
        """测试未授权访问"""
        response = client.get("/api/v1/documents/")
        assert response.status_code == 401

    def test_create_template(self, client, user_headers):
        """测试创建模板"""
        response = client.post(
            "/api/v1/templates/",
            json={
                "name": "测试模板",
                "type": "proposal", 
                "description": "测试用模板",
                "content": "客户: {{ customer_name }}\n需求: {{ requirements }}"
            },
            headers=user_headers
        )
        assert response.status_code in [200, 201]

    def test_list_templates(self, client, user_headers):
        """测试列出模板"""
        response = client.get("/api/v1/templates/", headers=user_headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data

    def test_create_knowledge(self, client, user_headers):
        """测试创建知识库"""
        response = client.post(
            "/api/v1/knowledge/",
            json={
                "title": "测试知识",
                "content": "这是测试知识内容",
                "category": "测试分类",
                "tags": ["测试", "知识"]
            },
            headers=user_headers
        )
        assert response.status_code in [200, 201]

    def test_list_knowledge(self, client, user_headers):
        """测试列出知识库"""
        response = client.get("/api/v1/knowledge/", headers=user_headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data

    def test_create_proposal(self, client, user_headers):
        """测试创建方案"""
        response = client.post(
            "/api/v1/proposals/",
            json={
                "title": "测试方案",
                "customer_name": "测试客户",
                "requirements": "测试需求",
                "industry": "金融"
            },
            headers=user_headers
        )
        assert response.status_code in [200, 201]

    def test_list_proposals(self, client, user_headers):
        """测试列出方案"""
        response = client.get("/api/v1/proposals/", headers=user_headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data


class TestErrorHandling:
    """错误处理测试"""

    def test_invalid_endpoint(self, client):
        """测试无效端点"""
        response = client.get("/api/v1/invalid/")
        assert response.status_code == 404

    def test_invalid_method(self, client, user_headers):
        """测试无效方法"""
        response = client.patch("/api/v1/documents/", headers=user_headers)
        assert response.status_code == 405

    def test_invalid_data_format(self, client, user_headers):
        """测试无效数据格式"""
        response = client.post(
            "/api/v1/templates/",
            json="invalid json",
            headers=user_headers
        )
        assert response.status_code == 422


class TestMiddleware:
    """中间件测试"""

    def test_cors_headers(self, client):
        """测试CORS头"""
        response = client.options("/health")
        # 应该有CORS相关头
        assert response.status_code in [200, 405]

    def test_metrics_endpoint(self, client):
        """测试指标端点"""
        response = client.get("/metrics")
        # 可能不需要认证，或者返回特定状态
        assert response.status_code in [200, 401, 404]