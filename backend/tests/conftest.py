"""测试配置和共享fixtures"""
import pytest
import sys
import os
import shutil
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Ensure test-friendly directories after import
os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
from pathlib import Path

from app import main as app_main
app_main.init_db = lambda: None
from app.main import app
from app.core.database import get_db
from app.models.base import Base
from app.models import User, UserRole
from app.api.auth import get_password_hash

# 测试数据库配置 - 使用内存SQLite，StaticPool保证共享连接
SQLALCHEMY_DATABASE_URL = "sqlite://"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def prepare_temp_dirs():
    """Ensure temporary directories exist and clean up afterwards."""
    os.environ["CHROMA_PERSIST_DIRECTORY"] = "./test_chroma"
    os.environ["UPLOAD_DIR"] = "./test_uploads"
    os.environ["EXPORT_DIR"] = "./test_exports"
    for path in ("./test_chroma", "./test_uploads", "./test_exports"):
        Path(path).mkdir(parents=True, exist_ok=True)
    yield
    for path in ("./test_chroma", "./test_uploads", "./test_exports"):
        shutil.rmtree(path, ignore_errors=True)


@pytest.fixture(scope="function")
def test_db(request):
    """创建测试数据库"""
    # 使用唯一的内存数据库
    db_name = f"file:{request.node.name}?mode=memory&cache=shared"
    engine = create_engine(f"sqlite:///{db_name}", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    def override_get_db():
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
        app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_client(test_db):
    """创建测试客户端，并将 FastAPI 的 get_db 覆盖为当前 Session。"""

    def override():
        try:
            yield test_db
        finally:
            test_db.rollback()

    app.dependency_overrides[get_db] = override
    client = TestClient(app)
    try:
        yield client
    finally:
        app.dependency_overrides[get_db] = get_db


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


@pytest.fixture
def viewer_user(test_db: Session):
    """创建只读用户"""
    user = User(
        username="viewer",
        email="viewer@example.com",
        password_hash=get_password_hash("Viewer123Pass"),
        full_name="Viewer User",
        role=UserRole.VIEWER,
        is_active=1
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture
def viewer_token(test_client: TestClient, viewer_user):
    """获取查看者令牌"""
    response = test_client.post(
        "/api/v1/auth/login",
        data={"username": "viewer", "password": "Viewer123Pass"}
    )
    return response.json()["access_token"]


@pytest.fixture
def viewer_headers(viewer_token: str):
    """查看者认证头"""
    return {"Authorization": f"Bearer {viewer_token}"}
