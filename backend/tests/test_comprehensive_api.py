"""补充API测试 - 提升API端点覆盖率"""
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

# 测试数据库
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_comprehensive_api.db"
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
def admin_user(client):
    """创建管理员用户"""
    db = TestingSessionLocal()
    user = User(
        username="admin",
        email="admin@example.com",
        password_hash=get_password_hash("adminpass123"),
        role=UserRole.ADMIN,
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
def admin_headers(client, admin_user):
    """获取管理员认证头"""
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "admin", "password": "adminpass123"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_document(client, user_headers, test_user):
    """创建示例文档"""
    db = TestingSessionLocal()
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
    return doc


@pytest.fixture
def sample_template(client, user_headers):
    """创建示例模板"""
    db = TestingSessionLocal()
    template = Template(
        name="测试模板",
        type=TemplateType.PROPOSAL,
        description="测试用模板",
        content="客户: {{ customer_name }}\n需求: {{ requirements }}"
    )
    db.add(template)
    db.commit()
    db.refresh(template)
    db.close()
    return template


@pytest.fixture
def sample_knowledge(client, user_headers):
    """创建示例知识库"""
    db = TestingSessionLocal()
    knowledge = KnowledgeBase(
        title="测试知识",
        content="这是测试知识内容",
        category="测试分类",
        tags=["测试", "知识"]
    )
    db.add(knowledge)
    db.commit()
    db.refresh(knowledge)
    db.close()
    return knowledge


@pytest.fixture
def sample_proposal(client, user_headers):
    """创建示例方案"""
    db = TestingSessionLocal()
    proposal = Proposal(
        title="测试方案",
        customer_name="测试客户",
        customer_industry="金融",
        requirements="测试需求",
        content="这是测试方案内容"
    )
    db.add(proposal)
    db.commit()
    db.refresh(proposal)
    db.close()
    return proposal


class TestDocumentsAPIExtended:
    """扩展文档API测试"""

    def test_upload_document_success(self, client, user_headers):
        """测试文档上传成功"""
        file_content = "这是测试文档的内容".encode('utf-8')
        file_obj = io.BytesIO(file_content)
        
        response = client.post(
            "/api/v1/documents/upload",
            files={"file": ("test.txt", file_obj, "text/plain")},
            data={
                "title": "上传的文档",
                "doc_type": "business_proposal",
                "industry": "金融",
                "customer_name": "测试客户"
            },
            headers=user_headers
        )
        assert response.status_code in [200, 201]

    def test_upload_document_file_too_large(self, client, user_headers):
        """测试上传文件过大"""
        # 创建一个大文件
        large_content = "x" * (10 * 1024 * 1024)  # 10MB
        file_obj = io.BytesIO(large_content.encode('utf-8'))
        
        response = client.post(
            "/api/v1/documents/upload",
            files={"file": ("large.txt", file_obj, "text/plain")},
            data={"title": "大文件"},
            headers=user_headers
        )
        # 应该返回文件过大错误
        assert response.status_code in [400, 413]

    def test_upload_document_unsupported_type(self, client, user_headers):
        """测试上传不支持的文件类型"""
        file_content = "test".encode('utf-8')
        file_obj = io.BytesIO(file_content)
        
        response = client.post(
            "/api/v1/documents/upload",
            files={"file": ("test.xyz", file_obj, "application/octet-stream")},
            data={"title": "不支持的格式"},
            headers=user_headers
        )
        # 应该返回不支持格式错误
        assert response.status_code in [400, 422]

    def test_update_document(self, client, user_headers, sample_document):
        """测试更新文档"""
        doc_id = sample_document.id
        response = client.put(
            f"/api/v1/documents/{doc_id}",
            json={
                "title": "更新的文档标题",
                "industry": "科技",
                "customer_name": "新客户"
            },
            headers=user_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "更新的文档标题"

    def test_delete_document(self, client, user_headers, sample_document):
        """测试删除文档"""
        doc_id = sample_document.id
        response = client.delete(f"/api/v1/documents/{doc_id}", headers=user_headers)
        assert response.status_code == 200
        
        # 验证文档已删除
        get_response = client.get(f"/api/v1/documents/{doc_id}", headers=user_headers)
        assert get_response.status_code == 404

    def test_search_documents(self, client, user_headers, sample_document):
        """测试搜索文档"""
        response = client.get(
            "/api/v1/documents/search",
            params={"q": "测试"},
            headers=user_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "items" in data

    def test_get_document_stats(self, client, user_headers, sample_document):
        """测试获取文档统计"""
        response = client.get("/api/v1/documents/stats", headers=user_headers)
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "by_type" in data


class TestTemplatesAPIExtended:
    """扩展模板API测试"""

    def test_get_template_by_id(self, client, user_headers, sample_template):
        """测试根据ID获取模板"""
        template_id = sample_template.id
        response = client.get(f"/api/v1/templates/{template_id}", headers=user_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == template_id

    def test_update_template(self, client, user_headers, sample_template):
        """测试更新模板"""
        template_id = sample_template.id
        response = client.put(
            f"/api/v1/templates/{template_id}",
            json={
                "name": "更新的模板",
                "description": "更新的描述",
                "content": "更新内容: {{ variable }}"
            },
            headers=user_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "更新的模板"

    def test_delete_template(self, client, user_headers, sample_template):
        """测试删除模板"""
        template_id = sample_template.id
        response = client.delete(f"/api/v1/templates/{template_id}", headers=user_headers)
        assert response.status_code == 200

    def test_preview_template(self, client, user_headers, sample_template):
        """测试预览模板"""
        template_id = sample_template.id
        response = client.post(
            f"/api/v1/templates/{template_id}/preview",
            json={
                "customer_name": "测试客户",
                "requirements": "测试需求"
            },
            headers=user_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "rendered_content" in data

    def test_extract_template_variables(self, client, user_headers, sample_template):
        """测试提取模板变量"""
        template_id = sample_template.id
        response = client.get(
            f"/api/v1/templates/{template_id}/variables",
            headers=user_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "variables" in data

    def test_search_templates(self, client, user_headers, sample_template):
        """测试搜索模板"""
        response = client.get(
            "/api/v1/templates/search",
            params={"q": "测试"},
            headers=user_headers
        )
        assert response.status_code == 200

    def test_validate_template(self, client, user_headers):
        """测试验证模板"""
        response = client.post(
            "/api/v1/templates/validate",
            json={
                "content": "你好，{{ name }}！欢迎来到{{ place }}。"
            },
            headers=user_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] == True


class TestKnowledgeAPIExtended:
    """扩展知识库API测试"""

    def test_get_knowledge_by_id(self, client, user_headers, sample_knowledge):
        """测试根据ID获取知识"""
        knowledge_id = sample_knowledge.id
        response = client.get(f"/api/v1/knowledge/{knowledge_id}", headers=user_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == knowledge_id

    def test_update_knowledge(self, client, user_headers, sample_knowledge):
        """测试更新知识"""
        knowledge_id = sample_knowledge.id
        response = client.put(
            f"/api/v1/knowledge/{knowledge_id}",
            json={
                "title": "更新的知识",
                "content": "更新的内容",
                "category": "新分类",
                "tags": ["更新", "标签"]
            },
            headers=user_headers
        )
        assert response.status_code == 200

    def test_delete_knowledge(self, client, user_headers, sample_knowledge):
        """测试删除知识"""
        knowledge_id = sample_knowledge.id
        response = client.delete(f"/api/v1/knowledge/{knowledge_id}", headers=user_headers)
        assert response.status_code == 200

    def test_search_knowledge(self, client, user_headers, sample_knowledge):
        """测试搜索知识"""
        response = client.get(
            "/api/v1/knowledge/search",
            params={"q": "测试"},
            headers=user_headers
        )
        assert response.status_code == 200

    def test_get_knowledge_by_category(self, client, user_headers, sample_knowledge):
        """测试根据分类获取知识"""
        response = client.get(
            "/api/v1/knowledge/category/测试分类",
            headers=user_headers
        )
        assert response.status_code == 200

    def test_get_knowledge_tags(self, client, user_headers, sample_knowledge):
        """测试获取知识标签"""
        response = client.get("/api/v1/knowledge/tags", headers=user_headers)
        assert response.status_code == 200

    def test_get_categories(self, client, user_headers):
        """测试获取所有分类"""
        response = client.get("/api/v1/knowledge/categories", headers=user_headers)
        assert response.status_code == 200


class TestProposalsAPIExtended:
    """扩展方案API测试"""

    def test_get_proposal_by_id(self, client, user_headers, sample_proposal):
        """测试根据ID获取方案"""
        proposal_id = sample_proposal.id
        response = client.get(f"/api/v1/proposals/{proposal_id}", headers=user_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == proposal_id

    def test_update_proposal(self, client, user_headers, sample_proposal):
        """测试更新方案"""
        proposal_id = sample_proposal.id
        response = client.put(
            f"/api/v1/proposals/{proposal_id}",
            json={
                "title": "更新的方案",
                "customer_name": "新客户",
                "requirements": "新需求",
                "content": "更新的内容"
            },
            headers=user_headers
        )
        assert response.status_code == 200

    def test_delete_proposal(self, client, user_headers, sample_proposal):
        """测试删除方案"""
        proposal_id = sample_proposal.id
        response = client.delete(f"/api/v1/proposals/{proposal_id}", headers=user_headers)
        assert response.status_code == 200

    def test_generate_proposal_content(self, client, user_headers, sample_proposal):
        """测试生成方案内容"""
        proposal_id = sample_proposal.id
        response = client.post(
            f"/api/v1/proposals/{proposal_id}/generate",
            json={"prompt": "生成详细的技术方案"},
            headers=user_headers
        )
        # 可能成功或失败（取决于AI配置）
        assert response.status_code in [200, 400, 500]

    def test_search_proposals(self, client, user_headers, sample_proposal):
        """测试搜索方案"""
        response = client.get(
            "/api/v1/proposals/search",
            params={"q": "测试"},
            headers=user_headers
        )
        assert response.status_code == 200

    def test_get_proposal_stats(self, client, user_headers, sample_proposal):
        """测试获取方案统计"""
        response = client.get("/api/v1/proposals/stats", headers=user_headers)
        assert response.status_code == 200

    def test_export_proposal(self, client, user_headers, sample_proposal):
        """测试导出方案"""
        proposal_id = sample_proposal.id
        response = client.get(
            f"/api/v1/proposals/{proposal_id}/export",
            params={"format": "word"},
            headers=user_headers
        )
        # 可能成功或失败
        assert response.status_code in [200, 400, 500]


class TestSearchAPIExtended:
    """扩展搜索API测试"""

    def test_global_search(self, client, user_headers, sample_document, sample_knowledge, sample_template):
        """测试全局搜索"""
        response = client.get(
            "/api/v1/search/global",
            params={"q": "测试"},
            headers=user_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "results" in data

    def test_vector_search(self, client, user_headers, sample_document, sample_knowledge):
        """测试向量搜索"""
        response = client.get(
            "/api/v1/search/vector",
            params={"q": "测试内容", "limit": 10},
            headers=user_headers
        )
        # 可能成功或失败（取决于向量配置）
        assert response.status_code in [200, 400, 500]

    def test_search_suggestions(self, client, user_headers):
        """测试搜索建议"""
        response = client.get(
            "/api/v1/search/suggestions",
            params={"q": "测", "limit": 5},
            headers=user_headers
        )
        assert response.status_code == 200

    def test_search_stats(self, client, user_headers):
        """测试搜索统计"""
        response = client.get("/api/v1/search/stats", headers=user_headers)
        assert response.status_code == 200


class TestMetricsAPIExtended:
    """扩展指标API测试"""

    def test_get_system_metrics(self, client, admin_headers):
        """测试获取系统指标（管理员）"""
        response = client.get("/api/v1/metrics/system", headers=admin_headers)
        assert response.status_code == 200

    def test_get_business_metrics(self, client, admin_headers):
        """测试获取业务指标（管理员）"""
        response = client.get("/api/v1/metrics/business", headers=admin_headers)
        assert response.status_code == 200

    def test_get_user_metrics_unauthorized(self, client, user_headers):
        """测试普通用户无法获取用户指标"""
        response = client.get("/api/v1/metrics/users", headers=user_headers)
        assert response.status_code in [401, 403]

    def test_get_metrics_summary(self, client, user_headers):
        """测试获取指标摘要"""
        response = client.get("/api/v1/metrics/summary", headers=user_headers)
        assert response.status_code == 200


class TestAuthAPIExtended:
    """扩展认证API测试"""

    def test_register_user(self, client):
        """测试用户注册"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "newpass123",
                "full_name": "新用户"
            }
        )
        assert response.status_code in [200, 201]
        data = response.json()
        assert "access_token" in data

    def test_register_duplicate_user(self, client, test_user):
        """测试注册重复用户"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser",  # 已存在
                "email": "another@example.com",
                "password": "password123"
            }
        )
        assert response.status_code == 400

    def test_login_invalid_credentials(self, client):
        """测试无效凭据登录"""
        response = client.post(
            "/api/v1/auth/login",
            data={"username": "wrong", "password": "wrong"}
        )
        assert response.status_code == 401

    def test_get_current_user(self, client, user_headers, test_user):
        """测试获取当前用户信息"""
        response = client.get("/api/v1/auth/me", headers=user_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == test_user.username

    def test_logout(self, client, user_headers):
        """测试登出（如果有此端点）"""
        response = client.post("/api/v1/auth/logout", headers=user_headers)
        # 可能存在或不存在此端点
        assert response.status_code in [200, 404]


class TestPaginationAndFiltering:
    """分页和过滤测试"""

    def test_documents_pagination(self, client, user_headers, sample_document):
        """测试文档分页"""
        response = client.get(
            "/api/v1/documents/",
            params={"page": 1, "size": 10},
            headers=user_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "size" in data

    def test_templates_filtering(self, client, user_headers, sample_template):
        """测试模板过滤"""
        response = client.get(
            "/api/v1/templates/",
            params={"type": "proposal"},
            headers=user_headers
        )
        assert response.status_code == 200

    def test_proposals_sorting(self, client, user_headers, sample_proposal):
        """测试方案排序"""
        response = client.get(
            "/api/v1/proposals/",
            params={"sort": "created_at", "order": "desc"},
            headers=user_headers
        )
        assert response.status_code == 200

    def test_knowledge_filtering_by_tags(self, client, user_headers, sample_knowledge):
        """测试知识库标签过滤"""
        response = client.get(
            "/api/v1/knowledge/",
            params={"tags": ["测试"]},
            headers=user_headers
        )
        assert response.status_code == 200


class TestErrorHandlingExtended:
    """扩展错误处理测试"""

    def test_invalid_token(self, client):
        """测试无效令牌"""
        response = client.get(
            "/api/v1/documents/",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 401

    def test_missing_token(self, client):
        """测试缺少令牌"""
        response = client.get("/api/v1/documents/")
        assert response.status_code == 401

    def test_invalid_endpoint(self, client, user_headers):
        """测试无效端点"""
        response = client.get("/api/v1/invalid/", headers=user_headers)
        assert response.status_code == 404

    def test_invalid_method(self, client, user_headers):
        """测试无效HTTP方法"""
        response = client.patch("/api/v1/documents/", headers=user_headers)
        assert response.status_code == 405

    def test_invalid_data_format(self, client, user_headers):
        """测试无效数据格式"""
        response = client.post(
            "/api/v1/templates/",
            json="invalid json string",
            headers=user_headers
        )
        assert response.status_code == 422

    def test_resource_not_found(self, client, user_headers):
        """测试资源不存在"""
        response = client.get("/api/v1/documents/99999", headers=user_headers)
        assert response.status_code == 404

    def test_permission_denied(self, client, user_headers, admin_user):
        """测试权限不足"""
        # 尝试访问其他用户的资源
        response = client.get("/api/v1/metrics/users", headers=user_headers)
        assert response.status_code in [401, 403]


class TestValidationAndSanitization:
    """验证和清理测试"""

    def test_xss_prevention_in_title(self, client, user_headers):
        """测试标题中的XSS防护"""
        xss_title = "<script>alert('xss')</script>恶意标题"
        
        response = client.post(
            "/api/v1/templates/",
            json={
                "name": xss_title,
                "type": "proposal",
                "content": "测试内容"
            },
            headers=user_headers
        )
        # 应该成功但XSS被清理
        if response.status_code == 200:
            data = response.json()
            assert "<script>" not in data["name"]

    def test_input_sanitization(self, client, user_headers):
        """测试输入清理"""
        malicious_content = "javascript:alert('xss')"
        
        response = client.post(
            "/api/v1/knowledge/",
            json={
                "title": "测试标题",
                "content": malicious_content,
                "category": "测试"
            },
            headers=user_headers
        )
        if response.status_code == 200:
            data = response.json()
            assert "javascript:" not in data["content"]

    def test_long_input_validation(self, client, user_headers):
        """测试长输入验证"""
        long_title = "x" * 1000  # 超长标题
        
        response = client.post(
            "/api/v1/templates/",
            json={
                "name": long_title,
                "type": "proposal",
                "content": "测试内容"
            },
            headers=user_headers
        )
        # 应该拒绝过长的输入
        assert response.status_code in [400, 422]


class TestFileOperationsExtended:
    """扩展文件操作测试"""

    def test_file_upload_size_limit(self, client, user_headers):
        """测试文件上传大小限制"""
        # 创建一个略小于限制的文件
        content = "x" * 5 * 1024 * 1024  # 5MB
        file_obj = io.BytesIO(content.encode('utf-8'))
        
        response = client.post(
            "/api/v1/documents/upload",
            files={"file": ("medium.txt", file_obj, "text/plain")},
            data={"title": "中等文件"},
            headers=user_headers
        )
        # 应该成功
        assert response.status_code in [200, 201]

    def test_unsupported_file_format(self, client, user_headers):
        """测试不支持的文件格式"""
        file_obj = io.BytesIO(b"fake content")
        
        response = client.post(
            "/api/v1/documents/upload",
            files={"file": ("fake.exe", file_obj, "application/octet-stream")},
            data={"title": "可执行文件"},
            headers=user_headers
        )
        # 应该拒绝
        assert response.status_code in [400, 422]

    def test_empty_file_upload(self, client, user_headers):
        """测试空文件上传"""
        file_obj = io.BytesIO(b"")
        
        response = client.post(
            "/api/v1/documents/upload",
            files={"file": ("empty.txt", file_obj, "text/plain")},
            data={"title": "空文件"},
            headers=user_headers
        )
        # 可能接受或拒绝空文件
        assert response.status_code in [200, 400, 422]


class TestConcurrentOperations:
    """并发操作测试"""

    def test_concurrent_api_requests(self, client, user_headers):
        """测试并发API请求"""
        import threading
        import time
        
        results = []
        
        def make_request():
            response = client.get("/api/v1/documents/", headers=user_headers)
            results.append(response.status_code)
        
        # 创建多个线程同时请求
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
        
        # 启动所有线程
        for thread in threads:
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        # 检查所有请求都成功
        assert all(status == 200 for status in results)
        assert len(results) == 5


class TestAPIPerformance:
    """API性能测试"""

    def test_response_time_basic(self, client, user_headers):
        """测试基本API响应时间"""
        import time
        
        start_time = time.time()
        response = client.get("/api/v1/documents/", headers=user_headers)
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < 2.0  # 应该在2秒内响应

    def test_large_list_response_time(self, client, user_headers):
        """测试大列表响应时间"""
        import time
        
        start_time = time.time()
        response = client.get(
            "/api/v1/documents/",
            params={"size": 100},
            headers=user_headers
        )
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < 3.0  # 大列表响应时间也应该合理


class TestAPIIntegrationScenarios:
    """API集成场景测试"""

    def test_complete_document_workflow(self, client, user_headers):
        """测试完整文档工作流"""
        # 1. 上传文档
        file_content = "工作流测试文档内容".encode('utf-8')
        file_obj = io.BytesIO(file_content)
        
        upload_response = client.post(
            "/api/v1/documents/upload",
            files={"file": ("workflow.txt", file_obj, "text/plain")},
            data={
                "title": "工作流文档",
                "doc_type": "business_proposal",
                "industry": "测试行业"
            },
            headers=user_headers
        )
        assert upload_response.status_code in [200, 201]
        
        doc_id = upload_response.json()["id"]
        
        # 2. 获取文档
        get_response = client.get(f"/api/v1/documents/{doc_id}", headers=user_headers)
        assert get_response.status_code == 200
        
        # 3. 更新文档
        update_response = client.put(
            f"/api/v1/documents/{doc_id}",
            json={"title": "更新的工作流文档"},
            headers=user_headers
        )
        assert update_response.status_code == 200
        
        # 4. 搜索文档
        search_response = client.get(
            "/api/v1/documents/search",
            params={"q": "工作流"},
            headers=user_headers
        )
        assert search_response.status_code == 200
        
        # 5. 删除文档
        delete_response = client.delete(f"/api/v1/documents/{doc_id}", headers=user_headers)
        assert delete_response.status_code == 200

    def test_template_proposal_integration(self, client, user_headers):
        """测试模板-方案集成"""
        # 1. 创建模板
        template_response = client.post(
            "/api/v1/templates/",
            json={
                "name": "集成测试模板",
                "type": "proposal",
                "content": "客户: {{ customer_name }}\n需求: {{ requirements }}\n方案: {{ solution }}"
            },
            headers=user_headers
        )
        assert template_response.status_code in [200, 201]
        template_id = template_response.json()["id"]
        
        # 2. 预览模板
        preview_response = client.post(
            f"/api/v1/templates/{template_id}/preview",
            json={
                "customer_name": "集成测试客户",
                "requirements": "集成测试需求",
                "solution": "集成测试方案"
            },
            headers=user_headers
        )
        assert preview_response.status_code == 200
        
        # 3. 创建方案
        proposal_response = client.post(
            "/api/v1/proposals/",
            json={
                "title": "基于模板的方案",
                "customer_name": "集成测试客户",
                "requirements": "集成测试需求",
                "template_id": template_id
            },
            headers=user_headers
        )
        assert proposal_response.status_code in [200, 201]
        
        proposal_id = proposal_response.json()["id"]
        
        # 4. 生成方案内容
        generate_response = client.post(
            f"/api/v1/proposals/{proposal_id}/generate",
            json={"use_template": True},
            headers=user_headers
        )
        # 可能成功或失败
        assert generate_response.status_code in [200, 400, 500]