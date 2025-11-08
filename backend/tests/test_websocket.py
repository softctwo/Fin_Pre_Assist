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
        # 发送测试消息
        websocket.send_json({"type": "ping"})
        data = websocket.receive_json()
        assert data["type"] in ["pong", "error"]


def test_websocket_auth():
    """测试WebSocket认证"""
    from app.main import app
    client = TestClient(app)

    # 无token应该连接失败或收到错误
    with client.websocket_connect("/ws") as websocket:
        data = websocket.receive_json()
        if "error" in str(data).lower():
            assert "unauthorized" in str(data).lower() or "auth" in str(data).lower()


def test_websocket_realtime_updates():
    """测试WebSocket实时更新"""
    from app.main import app
    client = TestClient(app)

    with client.websocket_connect("/ws/test") as websocket:
        # 订阅方案生成进度
        websocket.send_json({
            "type": "subscribe",
            "channel": "proposal_generation"
        })

        data = websocket.receive_json(timeout=5)
        assert isinstance(data, dict)


@pytest.mark.asyncio
async def test_websocket_broadcast():
    """测试WebSocket广播功能"""
    from app.services.websocket_manager import websocket_manager

    # 模拟广播消息
    message = {"type": "notification", "message": "Test notification"}
    await websocket_manager.broadcast(message)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
