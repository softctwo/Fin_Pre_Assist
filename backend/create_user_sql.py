#!/usr/bin/env python3
"""
直接通过SQL创建默认用户
"""
import sqlite3
import hashlib
import os

def create_users_directly():
    """直接通过SQLite创建用户"""
    db_path = "test_config.db"

    # 删除已存在的数据库
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"🗑️  删除旧数据库: {db_path}")

    # 连接数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # 创建users表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(50) NOT NULL UNIQUE,
                email VARCHAR(100) NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                full_name VARCHAR(100),
                role VARCHAR(20) DEFAULT 'user',
                is_active INTEGER DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 创建管理员用户（使用简单的hash）
        admin_password = "admin123"
        admin_hash = hashlib.sha256(admin_password.encode()).hexdigest()

        cursor.execute('''
            INSERT INTO users (username, email, password_hash, full_name, role)
            VALUES (?, ?, ?, ?, ?)
        ''', ("admin", "admin@finpre.com", admin_hash, "系统管理员", "admin"))

        # 创建演示用户
        demo_password = "demo123"
        demo_hash = hashlib.sha256(demo_password.encode()).hexdigest()

        cursor.execute('''
            INSERT INTO users (username, email, password_hash, full_name, role)
            VALUES (?, ?, ?, ?, ?)
        ''', ("demo", "demo@finpre.com", demo_hash, "演示用户", "user"))

        conn.commit()

        print("✅ 用户创建成功！")
        print("\n📋 默认登录信息：")
        print("┌─────────────────────────────────────┐")
        print("│ 管理员账户：                         │")
        print("│ 用户名: admin                       │")
        print("│ 密码:   admin123                     │")
        print("│ 邮箱:   admin@finpre.com             │")
        print("│ 角色:   管理员                       │")
        print("├─────────────────────────────────────┤")
        print("│ 演示账户：                           │")
        print("│ 用户名: demo                        │")
        print("│ 密码:   demo123                      │")
        print("│ 邮箱:   demo@finpre.com              │")
        print("│ 角色:   普通用户                     │")
        print("└─────────────────────────────────────┘")
        print("\n⚠️  注意：这是临时解决方案，正式环境请修复bcrypt配置")

    except Exception as e:
        print(f"❌ 创建用户失败: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    create_users_directly()