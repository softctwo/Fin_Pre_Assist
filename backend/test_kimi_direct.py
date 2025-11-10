#!/usr/bin/env python3
"""
直接测试Kimi API连接
"""

import asyncio
import httpx
import os
from app.core.config import settings

async def test_kimi_direct():
    """直接测试Kimi API"""
    print("🔧 直接测试Kimi API连接")
    print("=" * 30)

    print(f"API Key: {settings.KIMI_API_KEY[:20]}...")
    print(f"Base URL: {settings.KIMI_BASE_URL}")
    print(f"Model: {settings.KIMI_MODEL}")

    payload = {
        "model": settings.KIMI_MODEL,
        "messages": [
            {"role": "system", "content": "你是一个专业的助手"},
            {"role": "user", "content": "请简单介绍一下你自己"}
        ],
        "temperature": 0.7,
        "max_tokens": 100,
        "stream": False
    }

    headers = {
        "Authorization": f"Bearer {settings.KIMI_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"{settings.KIMI_BASE_URL}/chat/completions",
                json=payload,
                headers=headers
            )

            print(f"状态码: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                message = data["choices"][0]["message"]
                content = message.get("content", "")
                print(f"✅ API调用成功!")
                print(f"📄 响应内容: {content}")
                return True
            else:
                print(f"❌ API调用失败: {response.status_code}")
                print(f"📄 错误响应: {response.text}")
                return False

    except Exception as e:
        print(f"❌ 连接失败: {str(e)}")
        return False

if __name__ == "__main__":
    asyncio.run(test_kimi_direct())