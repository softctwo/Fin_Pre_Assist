"""
WebSocket管理器
管理WebSocket连接、消息广播和实时通信
"""

from typing import List
from fastapi import WebSocket
from loguru import logger
import json


class WebSocketManager:
    """WebSocket连接管理器"""

    def __init__(self):
        self.active_connections: List[WebSocket] = []
        logger.info("WebSocket管理器初始化完成")

    async def connect(self, websocket: WebSocket, client_id: str = None):
        """接受WebSocket连接"""
        await websocket.accept()
        websocket.client_id = client_id
        self.active_connections.append(websocket)
        logger.info(f"WebSocket客户端连接: {client_id or 'anonymous'}, 当前连接数: {len(self.active_connections)}")

    async def disconnect(self, websocket: WebSocket):
        """断开WebSocket连接"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(
                f"WebSocket客户端断开: {getattr(websocket, 'client_id', 'anonymous')}, 当前连接数: {len(self.active_connections)}"
            )

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """发送个人消息"""
        try:
            await websocket.send_text(json.dumps(message))
            logger.debug(f"发送个人消息给 {getattr(websocket, 'client_id', 'anonymous')}: {message['type']}")
        except Exception as e:
            logger.error(f"发送个人消息失败: {e}")

    async def broadcast(self, message: dict):
        """广播消息给所有连接"""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"广播消息失败: {e}")
                disconnected.append(connection)

        # 清理断开的连接
        for conn in disconnected:
            await self.disconnect(conn)

        logger.debug(f"广播消息: {message['type']} 给 {len(self.active_connections)} 个客户端")

    async def send_to_client(self, client_id: str, message: dict):
        """发送消息给指定客户端"""
        for connection in self.active_connections:
            if getattr(connection, "client_id", None) == client_id:
                try:
                    await connection.send_text(json.dumps(message))
                    logger.debug(f"发送消息给客户端 {client_id}: {message['type']}")
                    return True
                except Exception as e:
                    logger.error(f"发送消息给客户端失败: {e}")
                    await self.disconnect(connection)
                    return False
        return False

    def get_connection_count(self) -> int:
        """获取当前连接数"""
        return len(self.active_connections)

    def get_active_clients(self) -> List[str]:
        """获取活跃客户端ID列表"""
        return [
            getattr(conn, "client_id", "anonymous") for conn in self.active_connections if hasattr(conn, "client_id")
        ]


# 全局WebSocket管理器实例
websocket_manager = WebSocketManager()
