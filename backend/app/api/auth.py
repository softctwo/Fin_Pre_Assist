from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
import hashlib

from app.core.database import get_db
from app.core.config import settings
from app.models import User, UserRole
from app.api.simple_auth import (
    SIMPLE_USERS, create_simple_token, verify_simple_token,
    verify_simple_password, create_simple_password_hash, get_simple_user
)

router = APIRouter()

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_PREFIX}/auth/login")


# Pydantic模型
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str]
    role: UserRole
    is_active: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


# 密码工具函数 - 使用简化的SHA256方式
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码 - 使用SHA256"""
    return verify_simple_password(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """生成密码哈希 - 使用SHA256"""
    return create_simple_password_hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """根据用户名获取用户"""
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """根据邮箱获取用户"""
    return db.query(User).filter(User.email == email).first()


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """认证用户"""
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """获取当前用户 - 支持简化token验证"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的认证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # 首先尝试简化token验证
    simple_username = verify_simple_token(token)
    if simple_username and get_simple_user(simple_username):
        # 返回简化的用户对象
        simple_user = get_simple_user(simple_username)
        from collections import namedtuple
        UserLike = namedtuple('UserLike', ['id', 'username', 'email', 'full_name', 'role', 'is_active'])
        return UserLike(
            id=0,  # 简化用户使用固定ID
            username=simple_user['username'],
            email=simple_user['email'],
            full_name=simple_user['full_name'],
            role=simple_user['role'],
            is_active=1
        )

    # 如果简化token验证失败，尝试数据库JWT验证（兼容性）
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception

    user = get_user_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user = Depends(get_current_user)):
    """获取当前活跃用户"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="用户已被禁用")
    return current_user


# API端点
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """用户注册"""
    # 检查用户名是否已存在
    if get_user_by_username(db, user_data.username):
        raise HTTPException(status_code=400, detail="用户名已存在")

    # 检查邮箱是否已存在
    if get_user_by_email(db, user_data.email):
        raise HTTPException(status_code=400, detail="邮箱已被注册")

    # 创建新用户
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=hashed_password,
        full_name=user_data.full_name,
        role=UserRole.USER,
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """用户登录 - 使用简化认证"""
    # 首先检查简化用户数据库
    simple_user = get_simple_user(form_data.username)
    if simple_user:
        if verify_simple_password(form_data.password, simple_user["password_hash"]):
            # 创建访问令牌
            access_token = create_simple_token(form_data.username)
            return {"access_token": access_token, "token_type": "bearer"}

    # 如果简化用户中没有，尝试数据库用户（兼容性）
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 创建访问令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user = Depends(get_current_active_user)):
    """获取当前用户信息"""
    # 检查是否为简化用户对象
    if hasattr(current_user, 'role') and isinstance(current_user.role, str):
        # 简化用户对象，转换为UserResponse格式
        from datetime import datetime
        user_dict = {
            "id": 0,  # 简化用户没有数据库ID
            "username": current_user.username,
            "email": current_user.email,
            "full_name": current_user.full_name,
            "role": current_user.role,
            "is_active": current_user.is_active,
            "created_at": datetime.now()
        }

        # 创建UserResponse对象
        class SimpleUserResponse:
            def __init__(self, **kwargs):
                for k, v in kwargs.items():
                    setattr(self, k, v)

        return SimpleUserResponse(**user_dict)

    # 数据库用户，直接返回
    return current_user
