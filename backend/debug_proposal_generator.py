#!/usr/bin/env python3
"""
调试方案生成器
"""
import asyncio
import sys
import os

# 添加项目路径到系统路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.ai_service import ai_service
from app.models import Proposal
from app.services.proposal_generator import ProposalGenerator

class MockDB:
    """模拟数据库会话"""
    pass

async def debug_ai_generation():
    """调试AI生成"""
    print("🔧 开始调试AI生成...")
    print(f"当前AI提供商: {ai_service.provider}")

    # 测试一个简单的prompt
    try:
        print("📝 测试简单prompt...")
        result = await ai_service.generate_text("请简单介绍一下人工智能", temperature=0.7, max_tokens=100)
        print(f"✅ 简单prompt成功，长度: {len(result)}")
        print(f"内容预览: {result[:100]}...")
    except Exception as e:
        print(f"❌ 简单prompt失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return

    # 测试一个更复杂的prompt（类似方案生成器使用的）
    try:
        print("\n📝 测试复杂prompt...")
        complex_prompt = """你是一位资深的金融行业售前方案专家。

【任务】
为"测试银行"撰写一份专业的执行摘要（Executive Summary）。

【背景信息】
客户名称: 测试银行
所属行业: 金融
需求: 建设智能风控系统

【要求】
1. 字数控制在200-300字
2. 使用专业、简洁的商务语言
3. 突出价值主张和核心优势

请直接输出执行摘要内容："""

        print("开始生成复杂内容...")
        result = await ai_service.generate_text(complex_prompt, temperature=0.7, max_tokens=500)
        print(f"✅ 复杂prompt成功，长度: {len(result)}")
        print(f"内容预览: {result[:200]}...")
    except Exception as e:
        print(f"❌ 复杂prompt失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return

async def debug_proposal_generator():
    """调试方案生成器"""
    print("\n🔧 开始调试方案生成器...")

    # 创建模拟方案对象
    proposal = Proposal()
    proposal.id = 1
    proposal.title = "智能风控系统建设方案"
    proposal.customer_name = "测试银行"
    proposal.customer_industry = "金融"
    proposal.requirements = """
    某银行需要建设智能风控系统，包括：
    1. 实时交易风险监控
    2. 反欺诈模型建设
    3. 信用评分系统升级
    4. 风险数据可视化平台
    """

    # 创建方案生成器
    generator = ProposalGenerator(MockDB())

    try:
        print("📝 测试上下文构建...")
        similar_docs = []
        relevant_knowledge = []
        context = generator._build_enhanced_context(proposal, similar_docs, relevant_knowledge)
        print(f"✅ 上下文构建成功，长度: {len(context)}")

        print("\n📝 测试执行摘要生成...")
        executive_summary = await generator._generate_executive_summary(proposal, context)
        print(f"✅ 执行摘要生成成功，长度: {len(executive_summary)}")
        print(f"内容预览: {executive_summary[:200]}...")

    except Exception as e:
        print(f"❌ 方案生成器测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

async def main():
    """主函数"""
    print("🚀 开始调试...")
    print("=" * 60)

    # 1. 调试AI生成
    await debug_ai_generation()

    # 2. 调试方案生成器
    await debug_proposal_generator()

if __name__ == "__main__":
    asyncio.run(main())