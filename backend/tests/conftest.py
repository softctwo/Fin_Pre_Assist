"""测试配置"""
import pytest
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """设置测试环境"""
    # 设置测试环境变量
    os.environ["DATABASE_URL"] = "sqlite:///./test.db"
    os.environ["CHROMA_PERSIST_DIRECTORY"] = "./test_chroma"
    os.environ["UPLOAD_DIR"] = "./test_uploads"
    os.environ["EXPORT_DIR"] = "./test_exports"

    yield

    # 清理测试环境
    import shutil
    for dir_path in ["./test_chroma", "./test_uploads", "./test_exports"]:
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)

    if os.path.exists("./test.db"):
        os.remove("./test.db")
