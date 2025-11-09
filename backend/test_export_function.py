#!/usr/bin/env python3
"""
测试导出功能
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

async def test_export(token: str, proposal_id: int = 2, format: str = "docx"):
    """测试导出功能"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    print(f"\n🚀 开始测试导出功能，ID: {proposal_id}, 格式: {format}")

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                f"http://localhost:8000/api/v1/proposals/{proposal_id}/export?format={format}",
                headers=headers
            )

            print(f"📊 响应状态码: {response.status_code}")
            print(f"📄 响应头: {dict(response.headers)}")

            if response.status_code == 200:
                # 检查是否是文件下载
                content_type = response.headers.get("content-type", "")
                if "application/" in content_type:
                    print(f"✅ 导出成功! 文件类型: {content_type}")
                    print(f"📁 文件大小: {len(response.content)} bytes")

                    # 保存文件以验证
                    filename = f"test_export_{format}"
                    if format == "docx":
                        filename += ".docx"
                    elif format == "pdf":
                        filename += ".pdf"
                    elif format == "xlsx":
                        filename += ".xlsx"

                    with open(filename, "wb") as f:
                        f.write(response.content)
                    print(f"💾 文件已保存为: {filename}")
                    return True
                else:
                    print(f"❌ 响应不是文件格式: {content_type}")
                    print(f"📄 响应内容: {response.text[:500]}...")
                    return False
            else:
                error_text = response.text
                print(f"❌ 导出失败: {response.status_code}")
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
        print(f"❌ 导出超时 (30秒)")
        return False
    except Exception as e:
        print(f"❌ 导出异常: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_proposal_details(token: str, proposal_id: int = 2):
    """测试获取方案详情"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    print(f"\n🔍 检查方案详情，ID: {proposal_id}")

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                f"http://localhost:8000/api/v1/proposals/{proposal_id}",
                headers=headers
            )

            print(f"📊 响应状态码: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                print(f"✅ 方案详情获取成功!")
                print(f"📋 方案标题: {data.get('title', 'N/A')}")
                print(f"📊 状态: {data.get('status', 'N/A')}")
                print(f"📝 执行摘要: {'已生成' if data.get('executive_summary') else '未生成'}")
                print(f"💡 解决方案: {'已生成' if data.get('solution_overview') else '未生成'}")
                print(f"🔧 技术细节: {'已生成' if data.get('technical_details') else '未生成'}")
                print(f"📅 实施计划: {'已生成' if data.get('implementation_plan') else '未生成'}")
                print(f"💰 报价信息: {'已生成' if data.get('pricing') else '未生成'}")

                return data.get('status')
            else:
                print(f"❌ 获取方案详情失败: {response.status_code}")
                print(f"📄 错误详情: {response.text}")
                return None

    except Exception as e:
        print(f"❌ 获取方案详情异常: {str(e)}")
        return None

async def main():
    """主函数"""
    print("🚀 开始测试导出功能...")
    print("=" * 60)

    # 1. 登录获取token
    token = await login_and_get_token()
    if not token:
        print("\n❌ 登录失败，停止测试")
        return

    # 2. 检查方案详情和状态
    status = await test_proposal_details(token, 2)

    if status != "completed":
        print(f"\n⚠️  方案状态不是completed，可能影响导出: {status}")
        print("💡 尝试重新生成方案...")
        # 尝试重新生成方案
        try:
            async with httpx.AsyncClient(timeout=180) as client:
                response = await client.post(
                    f"http://localhost:8000/api/v1/proposals/2/generate",
                    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
                )
                if response.status_code == 200:
                    print("✅ 方案重新生成成功")
                    await asyncio.sleep(2)  # 等待2秒
                else:
                    print(f"❌ 方案重新生成失败: {response.status_code}")
        except Exception as e:
            print(f"❌ 方案重新生成异常: {str(e)}")

    # 3. 测试不同格式的导出
    formats = ["docx", "pdf", "xlsx"]
    results = {}

    for format in formats:
        print(f"\n" + "="*50)
        print(f"测试 {format.upper()} 格式导出")
        print("="*50)
        results[format] = await test_export(token, 2, format)

    # 4. 总结
    print(f"\n" + "="*50)
    print(f"测试结果总结")
    print("="*50)

    success_count = sum(results.values())
    total_count = len(formats)

    print(f"✅ 成功: {success_count}/{total_count}")
    for format, success in results.items():
        status = "✅" if success else "❌"
        print(f"{status} {format.upper()}: {'成功' if success else '失败'}")

    if success_count == total_count:
        print(f"\n🎉 所有导出功能测试成功！")
    elif success_count > 0:
        print(f"\n⚠️  部分导出功能正常")
    else:
        print(f"\n❌ 所有导出功能都失败，需要进一步分析")

if __name__ == "__main__":
    asyncio.run(main())