#!/usr/bin/env python3
"""
Kimi API 简单测试
专门测试Kimi的集成效果
"""

import asyncio
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.ai_service import ai_service
from app.core.config import settings

async def test_kimi_simple():
    """简单测试Kimi功能"""
    print("🚀 Kimi API 简单测试")
    print("=" * 30)

    try:
        # 设置为Kimi提供商
        ai_service.provider = "kimi"
        print(f"当前提供商: {ai_service.provider}")
        print(f"当前模型: {ai_service._resolve_model()}")

        # 打印配置
        print(f"\n🔧 配置信息:")
        print(f"KIMI_API_KEY: {settings.KIMI_API_KEY[:20]}...")
        print(f"KIMI_MODEL: {settings.KIMI_MODEL}")
        print(f"KIMI_BASE_URL: {settings.KIMI_BASE_URL}")

        # 测试1: 基本文本生成
        print("\n📝 测试1: 基本文本生成")
        prompt = "请用一句话介绍Kimi大模型"
        result = await ai_service.generate_text(prompt)
        print(f"✅ 成功: {result}")

        # 测试2: 长文本生成
        print("\n📝 测试2: 长文本生成")
        prompt = "请详细介绍金融科技在银行业的应用场景"
        result = await ai_service.generate_text(prompt, max_tokens=300)
        print(f"✅ 成功: {result[:100]}...")

        # 测试3: 向量化（应该使用zhipu）
        print("\n📝 测试3: 向量化功能")
        test_text = "测试向量化功能的文本内容"
        embedding = await ai_service.embed_text(test_text)
        print(f"✅ 成功: 向量维度 {len(embedding)}")

        print("\n🎉 Kimi集成测试全部通过！")
        return True

    except Exception as e:
        import traceback
        print(f"❌ 测试失败: {str(e)}")
        print("详细错误信息:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_kimi_simple())