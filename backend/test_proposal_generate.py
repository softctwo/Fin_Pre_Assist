#!/usr/bin/env python3
"""
测试方案生成API
"""
import asyncio
import sys
import os
import json
import httpx

async def login_and_get_token():
    """登录并获取token"""
    login_data = {
        "username": "admin",
        "password": "admin123"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/v1/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )

        if response.status_code != 200:
            print(f"❌ 登录失败: {response.status_code} - {response.text}")
            return None

        data = response.json()
        token = data.get("access_token")
        print(f"✅ 登录成功，获得token: {token[:20]}...")
        return token

async def test_proposal_generation(token: str, proposal_id: int = 2):
    """测试方案生成"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    print(f"\n🚀 开始生成方案，ID: {proposal_id}")

    try:
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(
                f"http://localhost:8000/api/v1/proposals/{proposal_id}/generate",
                headers=headers
            )

            print(f"📊 响应状态码: {response.status_code}")
            print(f"📄 响应头: {dict(response.headers)}")

            if response.status_code == 200:
                data = response.json()
                print(f"✅ 方案生成成功!")
                print(f"📋 生成的方案内容:")
                print("-" * 50)

                # 显示生成的各个部分
                if "executive_summary" in data:
                    print(f"📝 执行摘要: {data['executive_summary'][:200]}...")
                if "solution_overview" in data:
                    print(f"💡 解决方案概述: {data['solution_overview'][:200]}...")
                if "technical_details" in data:
                    print(f"🔧 技术细节: {data['technical_details'][:200]}...")
                if "implementation_plan" in data:
                    print(f"📅 实施计划: {data['implementation_plan'][:200]}...")

                print("-" * 50)
                return True
            else:
                error_text = response.text
                print(f"❌ 方案生成失败: {response.status_code}")
                print(f"📄 错误详情: {error_text}")

                # 尝试解析JSON错误
                try:
                    error_data = response.json()
                    print(f"🔍 结构化错误信息:")
                    print(json.dumps(error_data, indent=2, ensure_ascii=False))
                except:
                    print(f"🔍 原始错误文本: {error_text}")

                return False

    except httpx.TimeoutException:
        print(f"❌ 方案生成超时 (120秒)")
        return False
    except Exception as e:
        print(f"❌ 方案生成异常: {str(e)}")
        return False

async def main():
    """主函数"""
    print("🚀 开始方案生成测试...")
    print("=" * 60)

    # 登录获取token
    token = await login_and_get_token()
    if not token:
        print("\n❌ 登录失败，停止测试")
        return

    # 测试方案生成
    generation_ok = await test_proposal_generation(token, 2)

    if generation_ok:
        print("\n🎉 方案生成功能测试成功！")
    else:
        print("\n❌ 方案生成功能测试失败，需要进一步分析")

if __name__ == "__main__":
    asyncio.run(main())