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
        element_data = message.get("data", {}).get("element", {})
        
        # データベースに保存
        element = DrawingElement(
            whiteboard_id=UUID(whiteboard_id),
            user_id=UUID(user_id),
            type=DrawingType(element_data.get("type")),
            x=element_data.get("x", 0),
            y=element_data.get("y", 0),
            width=element_data.get("width"),
            height=element_data.get("height"),
            end_x=element_data.get("endX"),
            end_y=element_data.get("endY"),
            points=element_data.get("points"),
            color=element_data.get("color", "#000000"),
            stroke_width=element_data.get("strokeWidth"),
            fill_color=element_data.get("fill"),
            text_content=element_data.get("text"),
            font_size=element_data.get("fontSize"),
            font_family=element_data.get("fontFamily")
        )
        
        db.add(element)
        db.commit()
        db.refresh(element)
        
        # 他のユーザーにブロードキャスト
        broadcast_message = {
            "type": "draw",
            "data": {
                "element": {
                    "id": str(element.id),
                    "type": element.type.value,
                    "x": element.x,
                    "y": element.y,
                    "width": element.width,
                    "height": element.height,
                    "endX": element.end_x,
                    "endY": element.end_y,
                    "points": element.points,
                    "color": element.color,
                    "strokeWidth": element.stroke_width,
                    "fill": element.fill_color,
                    "text": element.text_content,
                    "fontSize": element.font_size,
                    "fontFamily": element.font_family,
                }
            },
            "userId": user_id,
            "timestamp": message.get("timestamp", "")
        }
        
        await self.manager.broadcast_to_whiteboard(
            whiteboard_id, 
            broadcast_message, 
            exclude_user=user_id
        )
    
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
        element_id = message.get("data", {}).get("elementId")
        
        if element_id:
            # データベースから削除
            element = db.query(DrawingElement).filter(
                DrawingElement.id == UUID(element_id),
                DrawingElement.whiteboard_id == UUID(whiteboard_id)
            ).first()
            
            if element:
                db.delete(element)
                db.commit()
            
            # 他のユーザーにブロードキャスト
            await self.manager.broadcast_to_whiteboard(
                whiteboard_id, 
                message, 
                exclude_user=user_id
            )
    
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