#!/usr/bin/env python3
"""
初始化AI模型配置
"""

import asyncio
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.ai_model import AIModel, PRESET_MODEL_CONFIGS


async def create_preset_models():
    """创建预设模型配置"""
    db = next(get_db())
    
    try:
        print("开始创建预设AI模型配置...")
        
        for preset in PRESET_MODEL_CONFIGS:
            # 检查是否已存在
            existing = db.query(AIModel).filter(AIModel.name == preset["name"]).first()
            if existing:
                print(f"模型 {preset['name']} 已存在，跳过")
                continue
            
            # 创建新模型
            model = AIModel(**preset)
            model.is_enabled = False  # 预设模型默认不启用
            
            db.add(model)
            db.commit()
            db.refresh(model)
            
            print(f"✓ 创建模型: {model.name} ({model.provider})")
        
        print("\n预设模型创建完成！")
        
        # 显示所有模型
        models = db.query(AIModel).all()
        print(f"\n当前共 {len(models)} 个模型配置:")
        for model in models:
            status = "启用" if model.is_enabled else "禁用"
            default = "[默认]" if model.is_default else ""
            print(f"  - {model.name} ({model.provider}) - {status} {default}")
        
    except Exception as e:
        print(f"创建预设模型失败: {e}")
        db.rollback()
    finally:
        db.close()


async def create_default_openai_model():
    """创建默认OpenAI模型（如果配置了API密钥）"""
    from app.core.config import settings
    
    if not settings.OPENAI_API_KEY:
        print("未配置OPENAI_API_KEY，跳过创建默认模型")
        return
    
    db = next(get_db())
    
    try:
        # 检查是否已有OpenAI模型
        existing = db.query(AIModel).filter(
            AIModel.provider == "openai",
            AIModel.is_enabled == True
        ).first()
        
        if existing:
            print("已存在启用的OpenAI模型，跳过创建")
            return
        
        # 创建默认OpenAI模型
        model = AIModel(
            name="OpenAI GPT-3.5-Turbo",
            provider="openai",
            model_name="gpt-3.5-turbo",
            api_key=settings.OPENAI_API_KEY,
            base_url="https://api.openai.com/v1",
            max_tokens=4096,
            context_length=16385,
            temperature=0.7,
            description="OpenAI的GPT-3.5 Turbo模型",
            is_enabled=True,
            is_default=True
        )
        
        db.add(model)
        db.commit()
        db.refresh(model)
        
        print(f"✓ 创建默认OpenAI模型: {model.name}")
        
    except Exception as e:
        print(f"创建默认OpenAI模型失败: {e}")
        db.rollback()
    finally:
        db.close()


async def main():
    """主函数"""
    print("🤖 AI模型配置初始化")
    print("=" * 50)
    
    await create_preset_models()
    await create_default_openai_model()
    
    print("\n" + "=" * 50)
    print("初始化完成！")
    print("\n请访问 http://localhost:8000/docs/ai/models 配置AI模型")


if __name__ == "__main__":
    asyncio.run(main())
