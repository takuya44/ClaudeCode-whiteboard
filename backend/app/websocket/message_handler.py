from typing import Dict, Any
from sqlalchemy.orm import Session
from uuid import UUID
import json

from app.core.database import get_db
from app.models.whiteboard import DrawingElement, DrawingType
from app.websocket.connection_manager import ConnectionManager


class MessageHandler:
    """WebSocketメッセージ処理クラス"""
    
    def __init__(self, connection_manager: ConnectionManager):
        self.manager = connection_manager
    
    async def handle_message(
        self, 
        message: dict, 
        whiteboard_id: str, 
        user_id: str,
        db: Session
    ):
        """
        受信したメッセージをタイプに応じて処理
        
        Args:
            message: 受信したメッセージ
            whiteboard_id: ホワイトボードID
            user_id: ユーザーID
            db: データベースセッション
        """
        message_type = message.get("type")
        
        if message_type == "draw":
            await self.handle_drawing_update(message, whiteboard_id, user_id, db)
        elif message_type == "erase":
            await self.handle_erase(message, whiteboard_id, user_id, db)
        elif message_type == "cursor":
            await self.handle_cursor_update(message, whiteboard_id, user_id)
        elif message_type == "ping":
            await self.handle_ping(message, whiteboard_id, user_id)
        elif message_type == "drawing_event":
            await self.handle_drawing_event(message, whiteboard_id, user_id)
        else:
            print(f"Unknown message type: {message_type}")
    
    async def handle_drawing_update(
        self, 
        message: dict, 
        whiteboard_id: str, 
        user_id: str,
        db: Session
    ):
        """
        描画更新メッセージを処理
        
        Args:
            message: 描画更新メッセージ
            whiteboard_id: ホワイトボードID
            user_id: ユーザーID
            db: データベースセッション
        """
        print(f"Handling drawing update from user {user_id} on whiteboard {whiteboard_id}")
        
        # 一時的にデータベース保存をスキップし、ブロードキャストのみ行う
        await self.manager.broadcast_to_whiteboard(
            whiteboard_id, 
            message, 
            exclude_user=user_id
        )
        
        print(f"Broadcasting drawing update to whiteboard {whiteboard_id}")
    
    async def handle_erase(
        self, 
        message: dict, 
        whiteboard_id: str, 
        user_id: str,
        db: Session
    ):
        """
        消去メッセージを処理
        
        Args:
            message: 消去メッセージ
            whiteboard_id: ホワイトボードID
            user_id: ユーザーID
            db: データベースセッション
        """
        print(f"Handling erase from user {user_id} on whiteboard {whiteboard_id}")
        
        # 一時的にデータベース削除をスキップし、ブロードキャストのみ行う
        await self.manager.broadcast_to_whiteboard(
            whiteboard_id, 
            message, 
            exclude_user=user_id
        )
        
        print(f"Broadcasting erase to whiteboard {whiteboard_id}")
    
    async def handle_cursor_update(
        self, 
        message: dict, 
        whiteboard_id: str, 
        user_id: str
    ):
        """
        カーソル位置更新メッセージを処理（保存なし、リアルタイム配信のみ）
        
        Args:
            message: カーソル位置メッセージ
            whiteboard_id: ホワイトボードID
            user_id: ユーザーID
        """
        # 他のユーザーにブロードキャスト
        await self.manager.broadcast_to_whiteboard(
            whiteboard_id, 
            message, 
            exclude_user=user_id
        )
    
    async def handle_ping(
        self, 
        message: dict, 
        whiteboard_id: str, 
        user_id: str
    ):
        """
        Pingメッセージを処理（接続維持用）
        
        Args:
            message: Pingメッセージ
            whiteboard_id: ホワイトボードID
            user_id: ユーザーID
        """
        # Pongを返す
        pong_message = {
            "type": "pong",
            "timestamp": message.get("timestamp", "")
        }
        
        # 送信者にのみ返す
        connections = self.manager.active_connections.get(whiteboard_id, [])
        for connection in connections:
            if connection in self.manager.connection_info:
                conn_user_id, _ = self.manager.connection_info[connection]
                if conn_user_id == user_id:
                    await self.manager.send_personal_message(
                        json.dumps(pong_message), 
                        connection
                    )
                    break
    
    async def handle_drawing_event(
        self, 
        message: dict, 
        whiteboard_id: str, 
        user_id: str
    ):
        """
        描画イベントメッセージを処理（リアルタイム描画中のイベント）
        
        Args:
            message: 描画イベントメッセージ
            whiteboard_id: ホワイトボードID
            user_id: ユーザーID
        """
        # 他のユーザーにブロードキャスト（描画中のプレビュー用）
        await self.manager.broadcast_to_whiteboard(
            whiteboard_id, 
            message, 
            exclude_user=user_id
        )