#!/usr/bin/env python3
"""
多模型方案生成测试脚本
测试多模型同步生成和版本迭代功能
"""

import asyncio
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.multi_model_proposal_service import multi_model_proposal_service
from app.core.database import get_db
from app.models import Proposal, User, ProposalVersionStatus
from app.services.ai_service import ai_service
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_multi_model_service():
    """测试多模型服务基础功能"""
    print("🚀 测试多模型方案生成服务")
    print("=" * 50)

    try:
        # 1. 测试获取可用模型
        print("\n📋 步骤1: 获取可用模型")
        models = multi_model_proposal_service.get_available_models()
        print(f"✅ 可用模型数量: {len(models)}")
        for model in models:
            print(f"  - {model['name']}: {model['provider']} ({model['model']})")

        # 2. 测试AI服务切换
        print("\n🔄 步骤2: 测试AI服务切换")
        for model in models:
            ai_service.provider = model['provider']
            print(f"  ✅ 切换到 {model['name']}: {ai_service._resolve_model()}")

        # 3. 测试简单的文本生成
        print("\n📝 步骤3: 测试各模型文本生成")
        test_prompt = "请简单介绍一下金融科技的发展趋势，控制在100字以内"

        for model in models[:2]:  # 只测试前两个模型以节省时间
            try:
                ai_service.provider = model['provider']
                print(f"\n  🤖 测试 {model['name']}...")
                result = await ai_service.generate_text(test_prompt, max_tokens=150)
                print(f"    ✅ 成功: {result[:100]}...")
            except Exception as e:
                print(f"    ❌ 失败: {str(e)}")

        print("\n🎉 多模型服务测试完成!")
        return True

    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_database_models():
    """测试数据库模型"""
    print("\n🔍 测试数据库模型")
    print("=" * 30)

    try:
        db = next(get_db())

        # 检查User表
        user_count = db.query(User).count()
        print(f"✅ 用户表: {user_count} 个用户")

        # 检查Proposal表
        proposal_count = db.query(Proposal).count()
        print(f"✅ 方案表: {proposal_count} 个方案")

        # 检查ProposalVersion表
        version_count = db.query(ProposalVersion).count()
        print(f"✅ 方案版本表: {version_count} 个版本")

        # 如果有数据，显示详情
        if proposal_count > 0:
            proposals = db.query(Proposal).limit(3).all()
            print(f"\n📋 方案示例:")
            for proposal in proposals:
                print(f"  - {proposal.title} (ID: {proposal.id})")

        db.close()
        return True

    except Exception as e:
        print(f"❌ 数据库测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_proposal_version_workflow():
    """测试方案版本工作流程"""
    print("\n🔄 测试方案版本工作流程")
    print("=" * 30)

    try:
        db = next(get_db())

        # 查找测试用户
        test_user = db.query(User).first()
        if not test_user:
            print("❌ 没有找到测试用户")
            return False

        # 查找测试方案
        test_proposal = db.query(Proposal).filter(Proposal.user_id == test_user.id).first()
        if not test_proposal:
            print("❌ 没有找到测试方案")
            return False

        print(f"✅ 找到测试方案: {test_proposal.title} (ID: {test_proposal.id})")

        # 测试版本号生成
        next_version = multi_model_proposal_service._get_next_version_number(db, test_proposal.id)
        print(f"✅ 下一个版本号: {next_version}")

        # 模拟版本创建（不实际生成内容）
        from app.models.proposal_version import ProposalVersion
        test_version = ProposalVersion(
            proposal_id=test_proposal.id,
            version_number=next_version,
            title=f"{test_proposal.title} - 测试版本",
            customer_name=test_proposal.customer_name,
            model_provider="kimi",
            model_name="moonshot-v1-8k",
            status=ProposalVersionStatus.DRAFT,
            created_by=test_user.id,
            content={"test": "测试内容"}
        )

        db.add(test_version)
        db.commit()
        db.refresh(test_version)

        print(f"✅ 创建测试版本: {test_version.title} (ID: {test_version.id})")

        # 测试版本查询
        versions = db.query(ProposalVersion)\
            .filter(ProposalVersion.proposal_id == test_proposal.id)\
            .order_by(ProposalVersion.version_number.desc())\
            .all()

        print(f"✅ 查询到 {len(versions)} 个版本")

        db.close()
        return True

    except Exception as e:
        print(f"❌ 工作流程测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """主测试函数"""
    print("🎯 多模型方案生成系统测试")
    print("=" * 60)

    test_results = []

    # 测试1: 多模型服务
    test_results.append(await test_multi_model_service())

    # 测试2: 数据库模型
    test_results.append(test_database_models())

    # 测试3: 工作流程
    test_results.append(await test_proposal_version_workflow())

    # 总结
    print("\n" + "=" * 60)
    print("📊 测试总结")
    passed = sum(test_results)
    total = len(test_results)
    print(f"✅ 通过测试: {passed}/{total}")
    print(f"📈 通过率: {(passed/total)*100:.1f}%")

    if passed == total:
        print("\n🎉 所有测试通过！多模型方案生成系统准备就绪！")
        print("\n🔧 后续步骤:")
        print("1. 启动后端服务: python app/main.py")
        print("2. 访问API文档: http://localhost:8000/api/v1/docs")
        print("3. 测试多模型方案生成API")
        print("4. 实现前端UI界面")
    else:
        print(f"\n⚠️ {total-passed} 个测试失败，请检查错误信息")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️ 测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()