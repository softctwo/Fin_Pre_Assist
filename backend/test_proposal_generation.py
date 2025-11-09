#!/usr/bin/env python3
"""
测试真实的方案生成功能
"""
import asyncio
import sys
import os
import json
import httpx

# 添加项目路径到系统路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

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

async def create_proposal(token: str):
    """创建一个测试方案"""
    proposal_data = {
        "title": "智能风控系统建设方案",
        "customer_name": "测试银行",
        "customer_industry": "金融",
        "customer_contact": "test@example.com",
        "requirements": """
        某银行需要建设智能风控系统，包括：
        1. 实时交易风险监控
        2. 反欺诈模型建设
        3. 信用评分系统升级
        4. 风险数据可视化平台
        5. 监管合规报告自动化

        请提供详细的技术方案、实施计划和预算估算。
        """
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            "http://localhost:8000/api/v1/proposals/",
            json=proposal_data,
            headers=headers
        )

        if response.status_code not in [200, 201]:
            print(f"❌ 创建方案失败: {response.status_code} - {response.text}")
            return None

        data = response.json()
        proposal_id = data.get("id")
        print(f"✅ 方案创建成功，ID: {proposal_id}")
        return proposal_id

async def test_proposal_generation(token: str, proposal_id: int):
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

async def test_direct_ai_generation():
    """直接测试AI生成功能"""
    print(f"\n🤖 直接测试AI生成功能...")

    from app.services.ai_service import ai_service

    try:
        # 确保使用DeepSeek
        ai_service.provider = "deepseek"
        print(f"🔧 当前AI提供商: {ai_service.provider}")

        test_prompt = """
        请为某银行设计一个智能风控系统建设方案，包括：
        1. 实时交易风险监控系统
        2. 基于机器学习的反欺诈模型
        3. 新一代信用评分系统
        4. 风险数据可视化平台
        5. 监管合规自动化报告

        请提供技术架构、实施方案、预期效果和预算估算。
        """

        print(f"📝 开始生成内容...")
        result = await ai_service.generate_text(test_prompt, temperature=0.7, max_tokens=2000)

        print(f"✅ AI生成成功!")
        print(f"📄 生成内容长度: {len(result)} 字符")
        print(f"📋 内容预览:")
        print("-" * 50)
        print(result[:800] + "..." if len(result) > 800 else result)
        print("-" * 50)

        return True

    except Exception as e:
        print(f"❌ AI生成失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """主函数"""
    print("🚀 开始真实方案生成测试...")
    print("=" * 60)

    # 1. 直接测试AI生成
    ai_ok = await test_direct_ai_generation()

    if not ai_ok:
        print("\n❌ AI生成测试失败，停止后续测试")
        return

    # 2. 登录获取token
    token = await login_and_get_token()
    if not token:
        print("\n❌ 登录失败，停止测试")
        return

    # 3. 创建方案
    proposal_id = await create_proposal(token)
    if not proposal_id:
        print("\n❌ 创建方案失败，停止测试")
        return

    # 4. 测试方案生成
    generation_ok = await test_proposal_generation(token, proposal_id)

    if generation_ok:
        print("\n🎉 方案生成功能测试成功！")
    else:
        print("\n❌ 方案生成功能测试失败，需要进一步分析")

if __name__ == "__main__":
    asyncio.run(main())