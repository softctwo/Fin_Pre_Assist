"""
WebSocket API
提供WebSocket连接和实时通信功能
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from loguru import logger
import json
from typing import Optional

from app.services.websocket_manager import websocket_manager


router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: Optional[str] = Query(None)):
    """
    WebSocket主连接端点
    - 支持JWT认证（可选）
    - 处理基础消息收发
    - 自动处理断开连接
    """
    client_id = None

    try:
        # 如果有token，尝试认证
        if token:
            try:
                # 这里简化处理，实际应从token解析用户ID
                client_id = f"user_{token[:8]}"
            except Exception as e:
                logger.warning(f"WebSocket token验证失败: {e}")
                client_id = "anonymous"
        else:
            client_id = "anonymous"

        # 接受连接
        await websocket_manager.connect(websocket, client_id)

        # 发送连接确认
        await websocket_manager.send_personal_message(
            {"type": "connected", "message": "WebSocket连接已建立", "client_id": client_id}, websocket
        )

        # 持续接收消息
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)

                # 处理ping消息
                if message.get("type") == "ping":
                    await websocket_manager.send_personal_message(
                        {"type": "pong", "timestamp": message.get("timestamp")}, websocket
                    )
                    continue

                # 处理其他消息类型
                logger.info(f"收到消息 from {client_id}: {message}")

                # 回显消息（测试用）
                await websocket_manager.send_personal_message(
                    {"type": "echo", "original_message": message, "client_id": client_id}, websocket
                )

            except json.JSONDecodeError:
                logger.error(f"无效的消息格式 from {client_id}")
                await websocket_manager.send_personal_message({"type": "error", "message": "无效的消息格式"}, websocket)

    except WebSocketDisconnect:
        logger.info(f"WebSocket客户端断开连接: {client_id}")
        await websocket_manager.disconnect(websocket)

    except Exception as e:
        logger.error(f"WebSocket连接错误: {e}")
        await websocket_manager.disconnect(websocket)


@router.websocket("/ws/test")
async def websocket_test_endpoint(websocket: WebSocket):
    """
    WebSocket测试端点
    - 无需认证
    - 用于测试连接性
    - 简单的ping-pong测试
    """
    client_id = "test_client"

    try:
        await websocket_manager.connect(websocket, client_id)

        # 发送欢迎消息
        await websocket_manager.send_personal_message(
            {
                "type": "welcome",
                "message": "WebSocket测试连接已建立",
                "client_id": client_id,
                "available_commands": ["ping", "echo", "broadcast_test"],
            },
            websocket,
        )

        # 接收并处理消息
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            msg_type = message.get("type")

            if msg_type == "ping":
                await websocket_manager.send_personal_message(
                    {"type": "pong", "timestamp": message.get("timestamp"), "message": "Pong from server!"}, websocket
                )

            elif msg_type == "echo":
                await websocket_manager.send_personal_message(
                    {"type": "echo_response", "original_message": message.get("message", ""), "client_id": client_id},
                    websocket,
                )

            elif msg_type == "broadcast_test":
                await websocket_manager.broadcast(
                    {
                        "type": "broadcast_message",
                        "from": client_id,
                        "message": message.get("message", "Test broadcast"),
                        "timestamp": message.get("timestamp"),
                    }
                )

            else:
                await websocket_manager.send_personal_message(
                    {"type": "unknown_command", "message": f"Unknown command: {msg_type}"}, websocket
                )

    except WebSocketDisconnect:
        logger.info(f"测试客户端断开: {client_id}")
        await websocket_manager.disconnect(websocket)

    except Exception as e:
        logger.error(f"WebSocket测试端点错误: {e}")
        await websocket_manager.disconnect(websocket)


@router.post("/ws/broadcast")
async def broadcast_message(message: dict):
    """
    REST API端点 - 广播消息给所有WebSocket客户端
    - 用于服务器主动推送
    - 不需要WebSocket连接
    """
    try:
        await websocket_manager.broadcast(message)
        return {
            "status": "success",
            "message": "广播消息已发送",
            "connected_clients": websocket_manager.get_connection_count(),
        }
    except Exception as e:
        logger.error(f"广播消息失败: {e}")
        return {"status": "error", "message": f"广播失败: {str(e)}"}


@router.get("/ws/clients")
async def get_connected_clients():
    """
    获取当前连接的WebSocket客户端信息
    """
    return {
        "connection_count": websocket_manager.get_connection_count(),
        "active_clients": websocket_manager.get_active_clients(),
    }
