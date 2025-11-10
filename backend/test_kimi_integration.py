#!/usr/bin/env python3
"""
Kimi API 集成测试脚本
测试Kimi大模型的文本生成和向量化功能
"""

import asyncio
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.ai_service import ai_service
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_kimi_text_generation():
    """测试Kimi文本生成功能"""
    print("\n🔧 测试Kimi文本生成功能...")

    try:
        # 设置为Kimi提供商
        ai_service.provider = "kimi"
        print(f"当前AI提供商: {ai_service.provider}")
        print(f"当前模型: {ai_service._resolve_model()}")

        # 测试简单文本生成
        prompt = "请简单介绍一下金融科技的发展趋势"
        print(f"\n📝 测试提示: {prompt}")

        result_text = await ai_service.generate_text(prompt, temperature=0.7, max_tokens=500)

        print(f"✅ 文本生成成功!")
        print(f"📄 生成内容长度: {len(result_text)} 字符")
        print(f"🔍 生成内容预览: {result_text[:200]}...")

        return True

    except Exception as e:
        print(f"❌ 文本生成测试失败: {str(e)}")
        return False

async def test_kimi_embedding():
    """测试向量化功能（应该使用zhipu）"""
    print("\n🔧 测试Kimi模式下的向量化功能（应该fallback到zhipu）...")

    try:
        # 确保设置为Kimi提供商
        ai_service.provider = "kimi"

        # 测试文本向量化
        test_text = "这是一个用于测试向量化功能的示例文本"
        print(f"📝 测试文本: {test_text}")

        embedding = await ai_service.embed_text(test_text)

        print(f"✅ 向量化成功!")
        print(f"📊 向量维度: {len(embedding)}")
        print(f"🔍 向量前5个值: {embedding[:5]}")

        return True

    except Exception as e:
        print(f"❌ 向量化测试失败: {str(e)}")
        return False

async def test_kimi_vs_other_providers():
    """测试Kimi与其他提供商的对比"""
    print("\n🔧 测试不同AI提供商对比...")

    test_prompt = "请用一句话说明什么是数字化转型"
    providers = ["kimi", "zhipu", "deepseek"]

    results = {}

    for provider in providers:
        try:
            ai_service.provider = provider
            print(f"\n🤖 测试 {provider.upper()} 提供商...")

            result_text = await ai_service.generate_text(
                test_prompt, temperature=0.7, max_tokens=100
            )

            results[provider] = {
                "success": True,
                "text": result_text,
                "length": len(result_text)
            }

            print(f"✅ {provider} 测试成功 - 长度: {len(result_text)}")
            print(f"📄 内容: {result_text}")

        except Exception as e:
            results[provider] = {
                "success": False,
                "error": str(e)
            }
            print(f"❌ {provider} 测试失败: {str(e)}")

    return results

async def main():
    """主测试函数"""
    print("🚀 开始Kimi API集成测试")
    print("=" * 50)

    # 测试统计
    total_tests = 0
    passed_tests = 0

    # 测试1: Kimi文本生成
    total_tests += 1
    if await test_kimi_text_generation():
        passed_tests += 1

    # 测试2: 向量化功能
    total_tests += 1
    if await test_kimi_embedding():
        passed_tests += 1

    # 测试3: 多提供商对比
    total_tests += 1
    comparison_results = await test_kimi_vs_other_providers()
    if any(result.get("success", False) for result in comparison_results.values()):
        passed_tests += 1

    # 测试总结
    print("\n" + "=" * 50)
    print("📊 测试总结")
    print(f"✅ 通过测试: {passed_tests}/{total_tests}")
    print(f"📈 通过率: {(passed_tests/total_tests)*100:.1f}%")

    if passed_tests == total_tests:
        print("🎉 所有测试通过！Kimi API集成成功！")
    else:
        print("⚠️ 部分测试失败，请检查配置和API密钥")

    print("\n🔗 详细结果:")
    for provider, result in comparison_results.items():
        status = "✅" if result.get("success") else "❌"
        print(f"  {status} {provider.upper()}: {result.get('text', result.get('error', '未知错误'))[:50]}...")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️ 测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()