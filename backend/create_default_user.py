#!/usr/bin/env python3
"""
创建默认用户脚本
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 设置环境变量
os.environ['DATABASE_URL'] = 'sqlite:///./test_config.db'

from app.core.database import SessionLocal
from app.models import User, UserRole
from app.api.auth import get_password_hash

def create_default_users():
    """创建默认用户"""
    db = SessionLocal()
    try:
        # 检查是否已存在管理员用户
        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            # 创建管理员用户
            admin = User(
                username="admin",
                email="admin@finpre.com",
                password_hash=get_password_hash("Admin123Pass"),
                full_name="系统管理员",
                role=UserRole.ADMIN,
                is_active=1
            )
            db.add(admin)
            print("✅ 创建管理员用户成功")
        else:
            print("ℹ️  管理员用户已存在")

        # 检查是否已存在普通测试用户
        test_user = db.query(User).filter(User.username == "demo").first()
        if not test_user:
            # 创建演示用户
            demo = User(
                username="demo",
                email="demo@finpre.com",
                password_hash=get_password_hash("Demo123Pass"),
                full_name="演示用户",
                role=UserRole.USER,
                is_active=1
            )
            db.add(demo)
            print("✅ 创建演示用户成功")
        else:
            print("ℹ️  演示用户已存在")

        db.commit()
        print("\n🎉 默认用户创建完成！")
        print("\n📋 用户登录信息：")
        print("┌─────────────────────────────────────┐")
        print("│ 管理员账户：                         │")
        print("│ 用户名: admin                       │")
        print("│ 密码:   Admin123Pass                 │")
        print("│ 邮箱:   admin@finpre.com             │")
        print("│ 角色:   管理员                       │")
        print("├─────────────────────────────────────┤")
        print("│ 演示账户：                           │")
        print("│ 用户名: demo                        │")
        print("│ 密码:   Demo123Pass                  │")
        print("│ 邮箱:   demo@finpre.com              │")
        print("│ 角色:   普通用户                     │")
        print("└─────────────────────────────────────┘")

    except Exception as e:
        print(f"❌ 创建默认用户失败: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_default_users()