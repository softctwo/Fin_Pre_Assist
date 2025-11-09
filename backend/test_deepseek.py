#!/usr/bin/env python3
"""
测试DeepSeek API连接和方案生成功能
"""
import asyncio
import sys
import os

# 添加项目路径到系统路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.ai_service import ai_service
from app.core.config import settings

async def test_deepseek_connection():
    """测试DeepSeek API连接"""
    print("🔧 当前AI提供商:", settings.AI_PROVIDER)
    print("🔧 当前使用的模型:", ai_service._resolve_model())
    print("🔧 DeepSeek API Key:", "已配置" if settings.DEEPSEEK_API_KEY else "未配置")

    # 测试简单的文本生成
    try:
        print("\n📝 测试简单的文本生成...")
        test_prompt = "请简单介绍一下金融科技行业的发展趋势。"
        result = await ai_service.generate_text(test_prompt, temperature=0.7, max_tokens=500)
        print("✅ 文本生成成功!")
        print("📄 生成内容:")
        print("-" * 50)
        print(result)
        print("-" * 50)
        return True
    except Exception as e:
        print(f"❌ 文本生成失败: {str(e)}")
        return False

async def test_proposal_generation():
    """测试方案生成"""
    try:
        print("\n📋 测试方案生成...")
        proposal_prompt = """
        客户需求：某中小银行需要数字化转型方案，包括：
        1. 移动银行应用开发
        2. 风险管理系统升级
        3. 客户关系管理系统
        4. 数据分析平台建设

        请提供详细的技术方案和实施建议。
        """
        result = await ai_service.generate_text(proposal_prompt, temperature=0.7, max_tokens=1000)
        print("✅ 方案生成成功!")
        print("📋 生成的方案:")
        print("-" * 50)
        print(result[:1000] + "..." if len(result) > 1000 else result)
        print("-" * 50)
        return True
    except Exception as e:
        print(f"❌ 方案生成失败: {str(e)}")
        return False

async def main():
    """主函数"""
    print("🚀 开始测试DeepSeek API...")
    print("=" * 60)

    # 确保使用DeepSeek
    if ai_service.provider != "deepseek":
        print(f"⚠️  当前AI提供商是 {ai_service.provider}，正在切换到DeepSeek...")
        ai_service.provider = "deepseek"
        print(f"✅ 已切换到 {ai_service.provider}")

    # 测试连接
    connection_ok = await test_deepseek_connection()

    if connection_ok:
        # 测试方案生成
        proposal_ok = await test_proposal_generation()

        if proposal_ok:
            print("\n🎉 所有测试通过！DeepSeek API配置正确。")
        else:
            print("\n⚠️  连接测试通过，但方案生成测试失败。")
    else:
        print("\n❌ DeepSeek API连接测试失败，请检查配置。")
        print("\n💡 请检查以下配置:")
        print("   1. DEEPSEEK_API_KEY 是否正确")
        print("   2. 网络连接是否正常")
        print("   3. DeepSeek API 服务是否可用")

if __name__ == "__main__":
    asyncio.run(main())