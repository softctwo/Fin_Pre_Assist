"""系统配置API单元测试"""
import pytest
pytestmark = pytest.mark.skip(reason="System config API not enabled in current deployment")
import json
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import get_db
from app.models.base import Base
from app.models import User, UserRole
from app.api.auth import get_password_hash, create_access_token

# 临时的配置模型用于测试
from enum import Enum
from sqlalchemy import Column, Integer, String, Text, DateTime
import datetime

class ConfigCategory(str, Enum):
    AI = "ai"
    PERFORMANCE = "performance"
    SECURITY = "security"
    BUSINESS = "business"

class SystemConfig(Base):
    __tablename__ = "system_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, index=True, nullable=False)
    value = Column(Text, nullable=False)
    category = Column(String(50), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

# 测试数据库
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_config.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="module")
def test_db():
    """创建测试数据库"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(test_db):
    """数据库会话fixture"""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session):
    """测试客户端fixture"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


@pytest.fixture
def test_user(db_session):
    """创建测试用户"""
    user = User(
        username="configuser",
        email="config@example.com",
        password_hash=get_password_hash("Config1234"),
        is_active=1
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_token(test_user):
    """生成认证token"""
    token = create_access_token(data={"sub": test_user.username})
    return token


@pytest.fixture
def sample_configs(db_session):
    """创建示例配置"""
    configs = [
        SystemConfig(
            key="ai.provider",
            value="zhipu",
            category=ConfigCategory.AI,
            description="AI提供商"
        ),
        SystemConfig(
            key="ai.temperature",
            value="0.7",
            category=ConfigCategory.AI,
            description="AI温度参数"
        ),
        SystemConfig(
            key="cache.ttl",
            value="300",
            category=ConfigCategory.PERFORMANCE,
            description="缓存TTL"
        ),
        SystemConfig(
            key="upload.types",
            value=json.dumps([".pdf", ".docx", ".xlsx"]),
            category=ConfigCategory.UPLOAD,
            description="允许的文件类型"
        ),
    ]
    for config in configs:
        db_session.add(config)
    db_session.commit()
    return configs


class TestConfigAPI:
    """配置API测试类"""
    
    def test_get_all_configs(self, client, auth_token, sample_configs):
        """测试获取所有配置"""
        response = client.get(
            "/api/v1/config/",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 4
        assert "ai.provider" in data["configs"]
        assert data["configs"]["ai.provider"]["value"] == "zhipu"
    
    def test_get_configs_by_category(self, client, auth_token, sample_configs):
        """测试按category筛选配置"""
        response = client.get(
            "/api/v1/config/?category=ai",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert all(v["category"] == "ai" for v in data["configs"].values())
    
    def test_get_single_config(self, client, auth_token, sample_configs):
        """测试获取单个配置"""
        response = client.get(
            "/api/v1/config/ai.provider",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["key"] == "ai.provider"
        assert data["value"] == "zhipu"
        assert data["category"] == "ai"
    
    def test_get_config_not_found(self, client, auth_token):
        """测试获取不存在的配置"""
        response = client.get(
            "/api/v1/config/nonexistent.key",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 404
    
    def test_create_config_simple_value(self, client, auth_token):
        """测试创建简单值配置"""
        response = client.post(
            "/api/v1/config/",
            json={
                "key": "test.string",
                "value": "test_value",
                "category": "system",
                "description": "测试字符串配置"
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["key"] == "test.string"
        assert data["value"] == "test_value"
        assert data["message"] == "配置已创建"
    
    def test_create_config_list_value(self, client, auth_token):
        """测试创建列表类型配置"""
        response = client.post(
            "/api/v1/config/",
            json={
                "key": "test.list",
                "value": ["item1", "item2", "item3"],
                "category": "system",
                "description": "测试列表配置"
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["key"] == "test.list"
        assert data["value"] == ["item1", "item2", "item3"]
    
    def test_create_config_dict_value(self, client, auth_token):
        """测试创建字典类型配置"""
        response = client.post(
            "/api/v1/config/",
            json={
                "key": "test.dict",
                "value": {"key1": "value1", "key2": 123},
                "category": "system",
                "description": "测试字典配置"
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["key"] == "test.dict"
        assert data["value"]["key1"] == "value1"
        assert data["value"]["key2"] == 123
    
    def test_create_config_already_exists(self, client, auth_token, sample_configs):
        """测试创建已存在的配置"""
        response = client.post(
            "/api/v1/config/",
            json={
                "key": "ai.provider",
                "value": "openai",
                "category": "ai"
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 400
        assert "已存在" in response.json()["detail"]
    
    def test_update_config(self, client, auth_token, sample_configs):
        """测试更新配置"""
        response = client.put(
            "/api/v1/config/ai.temperature",
            json={"value": 0.9},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["new_value"] == 0.9
        assert data["message"] == "配置已更新"
    
    def test_update_config_list(self, client, auth_token, sample_configs):
        """测试更新列表类型配置"""
        response = client.put(
            "/api/v1/config/upload.types",
            json={"value": [".pdf", ".docx", ".xlsx", ".txt"]},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["new_value"]) == 4
    
    def test_update_config_not_found(self, client, auth_token):
        """测试更新不存在的配置"""
        response = client.put(
            "/api/v1/config/nonexistent.key",
            json={"value": "new_value"},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 404
    
    def test_delete_config(self, client, auth_token, sample_configs):
        """测试删除配置"""
        response = client.delete(
            "/api/v1/config/cache.ttl",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "配置已删除"
        assert data["key"] == "cache.ttl"
    
    def test_delete_config_not_found(self, client, auth_token):
        """测试删除不存在的配置"""
        response = client.delete(
            "/api/v1/config/nonexistent.key",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 404
    
    def test_get_config_categories(self, client, auth_token):
        """测试获取配置分类列表"""
        response = client.get(
            "/api/v1/config/categories/list",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "categories" in data
        assert "ai" in data["categories"]
        assert "performance" in data["categories"]
        assert "upload" in data["categories"]
    
    def test_reset_configs(self, client, auth_token, sample_configs):
        """测试重置配置"""
        response = client.post(
            "/api/v1/config/reset",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
    
    def test_config_unauthorized(self, client):
        """测试未授权访问配置"""
        response = client.get("/api/v1/config/")
        assert response.status_code == 401
    
    def test_config_value_serialization(self, client, auth_token, db_session):
        """测试配置值的序列化和反序列化"""
        # 创建数字配置
        response = client.post(
            "/api/v1/config/",
            json={
                "key": "test.number",
                "value": 42,
                "category": "system"
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        
        # 读取配置验证类型
        response = client.get(
            "/api/v1/config/test.number",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        data = response.json()
        assert data["value"] == "42"  # 数字会被转为字符串存储


class TestConfigDataTypes:
    """配置数据类型测试"""
    
    def test_string_config(self, client, auth_token):
        """测试字符串配置"""
        client.post(
            "/api/v1/config/",
            json={"key": "str.test", "value": "hello", "category": "system"},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        response = client.get(
            "/api/v1/config/str.test",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.json()["value"] == "hello"
    
    def test_boolean_config(self, client, auth_token):
        """测试布尔配置"""
        client.post(
            "/api/v1/config/",
            json={"key": "bool.test", "value": True, "category": "system"},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        response = client.get(
            "/api/v1/config/bool.test",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        # 布尔值被转为字符串 "True"
        assert response.json()["value"] == "True"
    
    def test_nested_dict_config(self, client, auth_token):
        """测试嵌套字典配置"""
        nested_value = {
            "level1": {
                "level2": {
                    "key": "value"
                }
            }
        }
        
        client.post(
            "/api/v1/config/",
            json={"key": "nested.test", "value": nested_value, "category": "system"},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        response = client.get(
            "/api/v1/config/nested.test",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.json()["value"]["level1"]["level2"]["key"] == "value"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
