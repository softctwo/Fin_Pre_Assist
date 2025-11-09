"""
简化的认证模块，绕过bcrypt问题
"""
import hashlib
from jose import jwt, JWTError, ExpiredSignatureError
from datetime import datetime, timedelta, timezone
from app.core.config import settings


# 简单的JWT处理
def create_simple_token(username: str) -> str:
    """创建简单的访问令牌"""
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": username,
        "exp": expire,
        "iat": datetime.now(timezone.utc)
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def verify_simple_token(token: str) -> str:
    """验证简单令牌并返回用户名"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username = payload.get("sub")
        if username:
            return username
    except (JWTError, ExpiredSignatureError):
        return None


# 简单的用户验证 - 使用SHA256
def verify_simple_password(plain_password: str, user_hash: str) -> bool:
    """验证简单密码哈希"""
    plain_hash = hashlib.sha256(plain_password.encode()).hexdigest()
    return plain_hash == user_hash


def create_simple_password_hash(password: str) -> str:
    """创建简单密码哈希"""
    return hashlib.sha256(password.encode()).hexdigest()


# 模拟用户数据库
SIMPLE_USERS = {
    "admin": {
        "username": "admin",
        "email": "admin@finpre.com",
        "password_hash": hashlib.sha256("admin123".encode()).hexdigest(),
        "full_name": "系统管理员",
        "role": "admin"
    },
    "demo": {
        "username": "demo",
        "email": "demo@finpre.com",
        "password_hash": hashlib.sha256("demo123".encode()).hexdigest(),
        "full_name": "演示用户",
        "role": "user"
    }
}


def get_simple_user(username: str):
    """获取简化用户信息"""
    return SIMPLE_USERS.get(username)