#!/usr/bin/env python3
"""
测试修正后的Zhipu AI API实现
"""
import asyncio
import sys
import os

# 添加项目路径到系统路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.ai_service import ai_service
from app.core.config import settings

async def test_zhipu_connection():
    """测试Zhipu API连接"""
    print("🔧 当前AI提供商:", ai_service.provider)
    print("🔧 Zhipu API Key:", "已配置" if settings.ZHIPU_API_KEY else "未配置")
    print("🔧 Zhipu 模型:", settings.ZHIPU_MODEL)

    # 测试简单的文本生成
    try:
        print("\n📝 测试Zhipu文本生成...")
        test_prompt = "请简单介绍一下人工智能的发展历史。"
        result = await ai_service.generate_text(test_prompt, temperature=0.7, max_tokens=500)
        print("✅ Zhipu文本生成成功!")
        print("📄 生成内容:")
        print("-" * 50)
        print(result[:500] + "..." if len(result) > 500 else result)
        print("-" * 50)
        return True
    except Exception as e:
        print(f"❌ Zhipu文本生成失败: {str(e)}")
        return False

async def test_zhipu_embedding():
    """测试Zhipu向量化"""
    try:
        print("\n🔢 测试Zhipu文本向量化...")
        test_text = "这是一个测试文本，用于验证向量化功能。"
        embedding = await ai_service.embed_text(test_text)
        print(f"✅ 向量化成功! 向量维度: {len(embedding)}")
        print(f"📊 向量前10个值: {embedding[:10]}")
        return True
    except Exception as e:
        print(f"❌ 向量化失败: {str(e)}")
        return False

async def main():
    """主函数"""
    print("🚀 开始测试修正后的Zhipu AI API...")
    print("=" * 60)

    # 切换到Zhipu
    if ai_service.provider != "zhipu":
        print(f"⚠️  当前AI提供商是 {ai_service.provider}，正在切换到Zhipu...")
        ai_service.provider = "zhipu"
        print(f"✅ 已切换到 {ai_service.provider}")

    # 测试文本生成
    generation_ok = await test_zhipu_connection()

    # 测试向量化
    embedding_ok = await test_zhipu_embedding()

    if generation_ok and embedding_ok:
        print("\n🎉 所有Zhipu AI测试通过！API实现修正成功。")
    elif generation_ok:
        print("\n⚠️  文本生成测试通过，但向量化测试失败。")
    else:
        print("\n❌ Zhipu AI测试失败，可能需要进一步调整。")
        print("\n💡 可能的问题:")
        print("   1. API Key格式不正确")
        print("   2. 模型名称不正确")
        print("   3. API端点地址变更")
        print("   4. 认证方式调整")

if __name__ == "__main__":
    asyncio.run(main())