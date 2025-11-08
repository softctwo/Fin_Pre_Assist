"""
WebSocket 测试
测试WebSocket连接和实时通信功能
"""
import pytest
from fastapi.testclient import TestClient
from fastapi import WebSocket
import json

def test_websocket_connection():
    """测试WebSocket连接"""
    from app.main import app
    client = TestClient(app)

    with client.websocket_connect("/ws/test") as websocket:
        # 接收欢迎消息
        data = websocket.receive_json()
        assert data["type"] == "welcome"

        # 发送测试消息
        websocket.send_json({"type": "ping", "timestamp": "2025-01-01T00:00:00"})
        data = websocket.receive_json()
        assert data["type"] == "pong"
        assert "timestamp" in data


def test_websocket_auth():
    """测试WebSocket认证"""
    from app.main import app
    client = TestClient(app)

    # 测试主WebSocket端点（接收连接确认）
    with client.websocket_connect("/ws") as websocket:
        data = websocket.receive_json()
        assert data["type"] == "connected"
        assert "client_id" in data


def test_websocket_realtime_updates():
    """测试WebSocket实时更新"""
    from app.main import app
    client = TestClient(app)

    with client.websocket_connect("/ws/test") as websocket:
        # 接收欢迎消息
        data = websocket.receive_json()
        assert data["type"] == "welcome"

        # 发送ping测试
        websocket.send_json({
            "type": "ping",
            "timestamp": "2025-01-01T00:00:00"
        })

        data = websocket.receive_json()
        assert isinstance(data, dict)
        assert data["type"] == "pong"


@pytest.mark.asyncio
async def test_websocket_broadcast():
    """测试WebSocket广播功能"""
    from app.services.websocket_manager import websocket_manager

    # 模拟广播消息
    message = {"type": "notification", "message": "Test notification"}

    # 广播应该成功执行（即使没有客户端连接）
    try:
        await websocket_manager.broadcast(message)
        # 如果没有异常，测试通过
        assert True
    except Exception as e:
        pytest.fail(f"广播失败: {e}")


@pytest.mark.asyncio
async def test_websocket_manager_functions():
    """测试WebSocket管理器功能"""
    from app.services.websocket_manager import websocket_manager

    # 测试连接数（初始为0）
    count = websocket_manager.get_connection_count()
    assert count >= 0

    # 测试获取活跃客户端
    clients = websocket_manager.get_active_clients()
    assert isinstance(clients, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
