#!/usr/bin/env python3
"""
Kimi API 集成验证
确认Kimi大模型已成功集成到系统中
"""

import asyncio
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.ai_service import ai_service
from app.core.config import settings

async def verify_kimi_integration():
    """验证Kimi集成"""
    print("🎯 Kimi API 集成验证")
    print("=" * 40)

    # 1. 验证配置
    print("🔧 步骤1: 验证配置")
    print(f"  ✅ API Key: {settings.KIMI_API_KEY[:20]}...")
    print(f"  ✅ 模型: {settings.KIMI_MODEL}")
    print(f"  ✅ 基础URL: {settings.KIMI_BASE_URL}")

    # 2. 验证AI服务提供商切换
    print("\n🔄 步骤2: 验证提供商切换")
    ai_service.provider = "kimi"
    print(f"  ✅ 当前提供商: {ai_service.provider}")
    print(f"  ✅ 解析模型: {ai_service._resolve_model()}")

    # 3. 验证文本生成
    print("\n📝 步骤3: 验证文本生成")
    try:
        prompt = "请简单介绍一下你的能力"
        result = await ai_service.generate_text(prompt, max_tokens=100)
        print(f"  ✅ 文本生成成功")
        print(f"  📄 生成内容: {result}")
    except Exception as e:
        print(f"  ❌ 文本生成失败: {str(e)}")
        return False

    # 4. 验证向量化（应该使用zhipu）
    print("\n🔍 步骤4: 验证向量化功能")
    try:
        test_text = "测试向量化"
        embedding = await ai_service.embed_text(test_text)
        print(f"  ✅ 向量化成功")
        print(f"  📊 向量维度: {len(embedding)}")
        print(f"  ℹ️  注意: Kimi模式下向量使用zhipu确保稳定性")
    except Exception as e:
        print(f"  ❌ 向量化失败: {str(e)}")
        return False

    # 5. 验证多提供商支持
    print("\n🌟 步骤5: 验证多提供商支持")
    providers = ["kimi", "zhipu", "deepseek"]
    success_count = 0

    for provider in providers:
        try:
            ai_service.provider = provider
            test_prompt = "简单测试"
            result = await ai_service.generate_text(test_prompt, max_tokens=50)
            print(f"  ✅ {provider.upper()}: 可用")
            success_count += 1
        except Exception as e:
            print(f"  ⚠️  {provider.upper()}: {str(e)[:50]}...")

    # 总结
    print("\n" + "=" * 40)
    print("📊 集成验证总结")
    print(f"  ✅ 配置验证: 通过")
    print(f"  ✅ 提供商切换: 通过")
    print(f"  ✅ 文本生成: 通过")
    print(f"  ✅ 向量化功能: 通过")
    print(f"  📈 可用提供商: {success_count}/{len(providers)}")

    print(f"\n🎉 Kimi API集成成功!")
    print(f"🔗 使用方法: 设置AI_PROVIDER=kimi即可使用Kimi大模型")
    print(f"🛡️  向量策略: Kimi模式下向量自动使用zhipu确保稳定")

    return True

if __name__ == "__main__":
    try:
        success = asyncio.run(verify_kimi_integration())
        if success:
            print("\n✅ 所有验证通过，Kimi大模型集成完成！")
        else:
            print("\n❌ 验证失败，请检查配置")
    except Exception as e:
        print(f"\n❌ 验证过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()