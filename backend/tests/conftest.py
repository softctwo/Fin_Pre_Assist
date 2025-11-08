"""测试配置和共享fixtures"""
import pytest
import sys
import os
import shutil
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import app
from app.core.database import Base, get_db
from app.models import User, UserRole
from app.api.auth import get_password_hash

# 测试数据库配置
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


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """设置测试环境"""
    # 设置测试环境变量
    os.environ["DATABASE_URL"] = "sqlite:///./test.db"
    os.environ["CHROMA_PERSIST_DIRECTORY"] = "./test_chroma"
    os.environ["UPLOAD_DIR"] = "./test_uploads"
    os.environ["EXPORT_DIR"] = "./test_exports"
    
    # 创建测试目录
    for dir_path in ["./test_chroma", "./test_uploads", "./test_exports"]:
        os.makedirs(dir_path, exist_ok=True)

    yield

    # 清理测试环境
    for dir_path in ["./test_chroma", "./test_uploads", "./test_exports"]:
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)

    if os.path.exists("./test.db"):
        os.remove("./test.db")


@pytest.fixture(scope="function")
def test_db():
    """创建测试数据库"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def test_client(test_db):
    """创建测试客户端"""
    return TestClient(app)


@pytest.fixture
def test_user(test_db: Session):
    """创建测试用户"""
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash=get_password_hash("Test123Pass"),
        full_name="Test User",
        role=UserRole.USER,
        is_active=1
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture
def admin_user(test_db: Session):
    """创建管理员用户"""
    user = User(
        username="admin",
        email="admin@example.com",
        password_hash=get_password_hash("Admin123Pass"),
        full_name="Admin User",
        role=UserRole.ADMIN,
        is_active=1
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture
def auth_token(test_client: TestClient, test_user):
    """获取认证令牌"""
    response = test_client.post(
        "/api/v1/auth/login",
        data={"username": "testuser", "password": "Test123Pass"}
    )
    return response.json()["access_token"]


@pytest.fixture
def auth_headers(auth_token: str):
    """获取认证头"""
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture
def admin_token(test_client: TestClient, admin_user):
    """获取管理员令牌"""
    response = test_client.post(
        "/api/v1/auth/login",
        data={"username": "admin", "password": "Admin123Pass"}
    )
    return response.json()["access_token"]


@pytest.fixture
def admin_headers(admin_token: str):
    """获取管理员认证头"""
    return {"Authorization": f"Bearer {admin_token}"}
