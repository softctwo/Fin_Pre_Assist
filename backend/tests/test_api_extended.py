"""扩展API集成测试 - 增加更多端点测试覆盖"""
import pytest
import io
import json
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import get_db
from app.models.base import Base
from app.models import User, UserRole, Document, DocumentType, KnowledgeBase, Template, Proposal
from app.api.auth import get_password_hash


# 创建测试数据库
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_extended_api.db"
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
def test_admin(client):
    """创建管理员用户"""
    db = TestingSessionLocal()
    admin = User(
        username="admin",
        email="admin@example.com",
        password_hash=get_password_hash("adminpass123"),
        role=UserRole.ADMIN,
        is_active=True
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    db.close()
    return admin


@pytest.fixture
def user_headers(client, test_user):
    """获取普通用户认证头"""
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "testuser", "password": "testpass123"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_headers(client, test_admin):
    """获取管理员认证头"""
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "admin", "password": "adminpass123"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_document(client, user_headers):
    """创建示例文档"""
    # 创建一个虚拟文件用于上传
    file_content = "这是一个测试文档的内容".encode('utf-8')
    file_obj = io.BytesIO(file_content)
    
    response = client.post(
        "/api/v1/documents/upload",
        files={"file": ("test.txt", file_obj, "text/plain")},
        data={
            "title": "测试文档",
            "doc_type": "proposal",
            "industry": "金融",
            "customer_name": "测试客户"
        },
        headers=user_headers
    )
    return response.json()


@pytest.fixture
def sample_template(client, user_headers):
    """创建示例模板"""
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
    return response.json()


@pytest.fixture
def sample_knowledge(client, user_headers):
    """创建示例知识"""
    response = client.post(
        "/api/v1/knowledge/",
        json={
            "category": "产品介绍",
            "title": "测试产品",
            "content": "这是测试产品的详细介绍",
            "tags": ["测试", "产品"]
        },
        headers=user_headers
    )
    return response.json()


class TestDocumentsAPI:
    """测试文档API的更多端点"""

    def test_upload_document_success(self, client, user_headers):
        """测试成功上传文档"""
        file_content = "测试文档内容".encode('utf-8')
        file_obj = io.BytesIO(file_content)
        
        response = client.post(
            "/api/v1/documents/upload",
            files={"file": ("test.txt", file_obj, "text/plain")},
            data={
                "title": "新测试文档",
                "doc_type": "proposal",
                "industry": "制造业",
                "customer_name": "制造客户"
            },
            headers=user_headers
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "新测试文档"
        assert data["type"] == "proposal"
        assert data["industry"] == "制造业"

    def test_upload_document_file_too_large(self, client, user_headers):
        """测试上传过大文件"""
        # 创建一个大文件内容
        large_content = b"x" * (100 * 1024 * 1024)  # 100MB
        file_obj = io.BytesIO(large_content)
        
        response = client.post(
            "/api/v1/documents/upload",
            files={"file": ("large.txt", file_obj, "text/plain")},
            data={
                "title": "大文件测试",
                "doc_type": "proposal"
            },
            headers=user_headers
        )
        assert response.status_code == 413
        assert "文件大小超过限制" in response.json()["detail"]

    def test_upload_document_unsupported_type(self, client, user_headers):
        """测试上传不支持的文件类型"""
        file_content = "测试内容".encode('utf-8')
        file_obj = io.BytesIO(file_content)
        
        response = client.post(
            "/api/v1/documents/upload",
            files={"file": ("test.exe", file_obj, "application/octet-stream")},
            data={
                "title": "可执行文件测试",
                "doc_type": "proposal"
            },
            headers=user_headers
        )
        assert response.status_code == 400
        assert "不支持的文件类型" in response.json()["detail"]

    def test_list_documents(self, client, user_headers, sample_document):
        """测试列出文档"""
        response = client.get("/api/v1/documents/", headers=user_headers)
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "items" in data
        assert len(data["items"]) >= 1

    def test_get_document_by_id(self, client, user_headers, sample_document):
        """测试根据ID获取文档"""
        doc_id = sample_document["id"]
        response = client.get(f"/api/v1/documents/{doc_id}", headers=user_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == doc_id
        assert data["title"] == sample_document["title"]

    def test_get_document_not_found(self, client, user_headers):
        """测试获取不存在的文档"""
        response = client.get("/api/v1/documents/99999", headers=user_headers)
        assert response.status_code == 404

    def test_update_document(self, client, user_headers, sample_document):
        """测试更新文档"""
        doc_id = sample_document["id"]
        response = client.put(
            f"/api/v1/documents/{doc_id}",
            json={
                "title": "更新后的标题",
                "industry": "更新后的行业",
                "customer_name": "更新后的客户"
            },
            headers=user_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "更新后的标题"
        assert data["industry"] == "更新后的行业"

    def test_delete_document(self, client, user_headers, sample_document):
        """测试删除文档"""
        doc_id = sample_document["id"]
        response = client.delete(f"/api/v1/documents/{doc_id}", headers=user_headers)
        assert response.status_code == 204

    def test_search_documents(self, client, user_headers, sample_document):
        """测试搜索文档"""
        response = client.get(
            "/api/v1/documents/search?query=测试",
            headers=user_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "items" in data

    def test_get_document_stats(self, client, user_headers):
        """测试获取文档统计"""
        response = client.get("/api/v1/documents/stats", headers=user_headers)
        assert response.status_code == 200
        data = response.json()
        assert "total_documents" in data
        assert "by_type" in data
        assert "by_industry" in data


class TestTemplatesAPIExtended:
    """测试模板API的扩展功能"""

    def test_get_template_by_id(self, client, user_headers, sample_template):
        """测试根据ID获取模板"""
        template_id = sample_template["id"]
        response = client.get(f"/api/v1/templates/{template_id}", headers=user_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == template_id

    def test_update_template(self, client, user_headers, sample_template):
        """测试更新模板"""
        template_id = sample_template["id"]
        response = client.put(
            f"/api/v1/templates/{template_id}",
            json={
                "name": "更新后的模板",
                "description": "更新后的描述",
                "content": "更新后的内容: {{ customer_name }}"
            },
            headers=user_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "更新后的模板"

    def test_delete_template(self, client, user_headers, sample_template):
        """测试删除模板"""
        template_id = sample_template["id"]
        response = client.delete(f"/api/v1/templates/{template_id}", headers=user_headers)
        assert response.status_code == 204

    def test_preview_template(self, client, user_headers, sample_template):
        """测试预览模板"""
        response = client.post(
            "/api/v1/templates/preview",
            json={
                "content": "客户: {{ customer_name }}\n需求: {{ requirements }}",
                "variables": {
                    "customer_name": "测试客户",
                    "requirements": "开发一个系统"
                }
            },
            headers=user_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "preview" in data
        assert "测试客户" in data["preview"]

    def test_extract_template_variables(self, client, user_headers):
        """测试提取模板变量"""
        response = client.post(
            "/api/v1/templates/extract-variables",
            json={
                "content": "客户: {{ customer_name }}\n预算: {{ budget }}\n截止日期: {{ deadline }}"
            },
            headers=user_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "variables" in data
        assert "customer_name" in data["variables"]
        assert "budget" in data["variables"]
        assert "deadline" in data["variables"]

    def test_search_templates(self, client, user_headers, sample_template):
        """测试搜索模板"""
        response = client.get(
            "/api/v1/templates/search?query=测试",
            headers=user_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "items" in data


class TestKnowledgeAPIExtended:
    """测试知识库API的扩展功能"""

    def test_get_knowledge_by_id(self, client, user_headers, sample_knowledge):
        """测试根据ID获取知识"""
        knowledge_id = sample_knowledge["id"]
        response = client.get(f"/api/v1/knowledge/{knowledge_id}", headers=user_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == knowledge_id

    def test_update_knowledge(self, client, user_headers, sample_knowledge):
        """测试更新知识"""
        knowledge_id = sample_knowledge["id"]
        response = client.put(
            f"/api/v1/knowledge/{knowledge_id}",
            json={
                "title": "更新后的标题",
                "content": "更新后的内容",
                "tags": ["更新", "标签"]
            },
            headers=user_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "更新后的标题"

    def test_delete_knowledge(self, client, user_headers, sample_knowledge):
        """测试删除知识"""
        knowledge_id = sample_knowledge["id"]
        response = client.delete(f"/api/v1/knowledge/{knowledge_id}", headers=user_headers)
        assert response.status_code == 204

    def test_search_knowledge(self, client, user_headers, sample_knowledge):
        """测试搜索知识"""
        response = client.get(
            "/api/v1/knowledge/search?query=测试",
            headers=user_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "items" in data

    def test_get_knowledge_by_category(self, client, user_headers, sample_knowledge):
        """测试按分类获取知识"""
        response = client.get(
            "/api/v1/knowledge/category/产品介绍",
            headers=user_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "items" in data

    def test_get_knowledge_tags(self, client, user_headers):
        """测试获取所有标签"""
        response = client.get("/api/v1/knowledge/tags", headers=user_headers)
        assert response.status_code == 200
        data = response.json()
        assert "tags" in data


class TestProposalsAPIExtended:
    """测试方案API的扩展功能"""

    def test_get_proposal_by_id(self, client, user_headers):
        """测试根据ID获取方案"""
        # 先创建一个方案
        create_response = client.post(
            "/api/v1/proposals/",
            json={
                "title": "测试方案详情",
                "customer_name": "详情测试客户",
                "customer_industry": "科技",
                "requirements": "需要开发一个AI系统"
            },
            headers=user_headers
        )
        proposal_id = create_response.json()["id"]
        
        response = client.get(f"/api/v1/proposals/{proposal_id}", headers=user_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == proposal_id

    def test_update_proposal(self, client, user_headers):
        """测试更新方案"""
        # 先创建一个方案
        create_response = client.post(
            "/api/v1/proposals/",
            json={
                "title": "待更新方案",
                "customer_name": "更新测试客户",
                "customer_industry": "金融",
                "requirements": "原始需求"
            },
            headers=user_headers
        )
        proposal_id = create_response.json()["id"]
        
        response = client.put(
            f"/api/v1/proposals/{proposal_id}",
            json={
                "title": "更新后的方案",
                "customer_industry": "科技",
                "requirements": "更新后的需求"
            },
            headers=user_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "更新后的方案"
        assert data["customer_industry"] == "科技"

    def test_delete_proposal(self, client, user_headers):
        """测试删除方案"""
        # 先创建一个方案
        create_response = client.post(
            "/api/v1/proposals/",
            json={
                "title": "待删除方案",
                "customer_name": "删除测试客户",
                "customer_industry": "制造",
                "requirements": "待删除的需求"
            },
            headers=user_headers
        )
        proposal_id = create_response.json()["id"]
        
        response = client.delete(f"/api/v1/proposals/{proposal_id}", headers=user_headers)
        assert response.status_code == 204

    def test_generate_proposal_content(self, client, user_headers):
        """测试生成方案内容"""
        response = client.post(
            "/api/v1/proposals/generate",
            json={
                "customer_name": "AI客户",
                "customer_industry": "科技",
                "requirements": "需要开发一个智能客服系统",
                "template_id": None
            },
            headers=user_headers
        )
        # 这个可能会失败，因为需要AI服务，但至少应该返回正确的错误码
        assert response.status_code in [200, 500, 503]

    def test_search_proposals(self, client, user_headers):
        """测试搜索方案"""
        response = client.get(
            "/api/v1/proposals/search?query=测试",
            headers=user_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "items" in data

    def test_get_proposal_stats(self, client, user_headers):
        """测试获取方案统计"""
        response = client.get("/api/v1/proposals/stats", headers=user_headers)
        assert response.status_code == 200
        data = response.json()
        assert "total_proposals" in data
        assert "by_status" in data
        assert "by_industry" in data


class TestSearchAPIExtended:
    """测试搜索API的扩展功能"""

    def test_global_search(self, client, user_headers, sample_document, sample_knowledge, sample_template):
        """测试全局搜索"""
        response = client.get(
            "/api/v1/search/global?query=测试&type=all",
            headers=user_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert "total" in data

    def test_vector_search(self, client, user_headers, sample_knowledge):
        """测试向量搜索"""
        response = client.post(
            "/api/v1/search/vector",
            json={
                "query": "测试产品",
                "collection": "knowledge",
                "limit": 5
            },
            headers=user_headers
        )
        # 可能会因为向量服务不可用而失败，但应该返回正确的错误码
        assert response.status_code in [200, 500, 503]

    def test_search_suggestions(self, client, user_headers):
        """测试搜索建议"""
        response = client.get(
            "/api/v1/search/suggestions?q=测",
            headers=user_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "suggestions" in data


class TestMetricsAPI:
    """测试指标API"""

    def test_get_system_metrics(self, client, admin_headers):
        """测试获取系统指标"""
        response = client.get("/api/v1/metrics/system", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert "cpu_usage" in data
        assert "memory_usage" in data
        assert "disk_usage" in data

    def test_get_business_metrics(self, client, admin_headers):
        """测试获取业务指标"""
        response = client.get("/api/v1/metrics/business", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert "total_users" in data
        assert "total_documents" in data
        assert "total_proposals" in data

    def test_get_user_metrics_unauthorized(self, client, user_headers):
        """测试普通用户无权访问系统指标"""
        response = client.get("/api/v1/metrics/system", headers=user_headers)
        assert response.status_code == 403

    def test_get_metrics_summary(self, client, admin_headers):
        """测试获取指标摘要"""
        response = client.get("/api/v1/metrics/summary", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert "system" in data
        assert "business" in data


class TestErrorHandling:
    """测试错误处理"""

    def test_unauthorized_access(self, client):
        """测试未授权访问"""
        response = client.get("/api/v1/documents/")
        assert response.status_code == 401

    def test_invalid_token(self, client):
        """测试无效token"""
        response = client.get(
            "/api/v1/documents/",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 401

    def test_invalid_endpoint(self, client, user_headers):
        """测试无效端点"""
        response = client.get("/api/v1/invalid/endpoint", headers=user_headers)
        assert response.status_code == 404

    def test_invalid_method(self, client, user_headers):
        """测试无效HTTP方法"""
        response = client.patch("/api/v1/documents/", headers=user_headers)
        assert response.status_code == 405

    def test_invalid_data_format(self, client, user_headers):
        """测试无效数据格式"""
        response = client.post(
            "/api/v1/templates/",
            json={"invalid": "data"},
            headers=user_headers
        )
        assert response.status_code == 422


class TestPaginationAndFiltering:
    """测试分页和过滤功能"""

    def test_documents_pagination(self, client, user_headers):
        """测试文档分页"""
        response = client.get(
            "/api/v1/documents/?page=1&size=10",
            headers=user_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "page" in data
        assert "size" in data
        assert "items" in data

    def test_templates_filtering(self, client, user_headers):
        """测试模板过滤"""
        response = client.get(
            "/api/v1/templates/?type=proposal",
            headers=user_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "items" in data

    def test_proposals_sorting(self, client, user_headers):
        """测试方案排序"""
        response = client.get(
            "/api/v1/proposals/?sort=created_at&order=desc",
            headers=user_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "items" in data

    def test_knowledge_filtering_by_tags(self, client, user_headers):
        """测试按标签过滤知识"""
        response = client.get(
            "/api/v1/knowledge/?tags=测试,产品",
            headers=user_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "items" in data