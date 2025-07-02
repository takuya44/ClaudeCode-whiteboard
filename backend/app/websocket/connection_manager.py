from typing import Dict, List, Set
from fastapi import WebSocket
from uuid import UUID
import json


class ConnectionManager:
    """WebSocket接続管理クラス"""
    
    def __init__(self):
        # whiteboard_id -> List[WebSocket]
        self.active_connections: Dict[str, List[WebSocket]] = {}
        # user_id -> Set[whiteboard_id]
        self.user_sessions: Dict[str, Set[str]] = {}
        # websocket -> (user_id, whiteboard_id)
        self.connection_info: Dict[WebSocket, tuple[str, str]] = {}
    
    async def connect(self, websocket: WebSocket, whiteboard_id: str, user_id: str):
        """
        WebSocket接続を受け入れて管理
        
        Args:
            websocket: WebSocket接続
            whiteboard_id: ホワイトボードID
            user_id: ユーザーID
        """
        await websocket.accept()
        
        # ホワイトボードの接続リストに追加
        if whiteboard_id not in self.active_connections:
            self.active_connections[whiteboard_id] = []
        self.active_connections[whiteboard_id].append(websocket)
        
        # ユーザーセッションに追加
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = set()
        self.user_sessions[user_id].add(whiteboard_id)
        
        # 接続情報を保存
        self.connection_info[websocket] = (user_id, whiteboard_id)
        
        # 他のユーザーに参加を通知
        await self.broadcast_to_whiteboard(
            whiteboard_id,
            {
                "type": "user_join",
                "data": {
                    "userId": user_id,
                    "timestamp": json.loads(json.dumps(str(UUID(user_id))))
                },
                "userId": user_id,
                "timestamp": ""
            },
            exclude_user=user_id
        )
    
    async def disconnect(self, websocket: WebSocket, whiteboard_id: str, user_id: str):
        """
        WebSocket接続を切断して管理から削除
        
        Args:
            websocket: WebSocket接続
            whiteboard_id: ホワイトボードID
            user_id: ユーザーID
        """
        # ホワイトボードの接続リストから削除
        if whiteboard_id in self.active_connections:
            self.active_connections[whiteboard_id].remove(websocket)
            if not self.active_connections[whiteboard_id]:
                del self.active_connections[whiteboard_id]
        
        # ユーザーセッションから削除
        if user_id in self.user_sessions:
            self.user_sessions[user_id].discard(whiteboard_id)
            if not self.user_sessions[user_id]:
                del self.user_sessions[user_id]
        
        # 接続情報を削除
        if websocket in self.connection_info:
            del self.connection_info[websocket]
        
        # 他のユーザーに離脱を通知
        await self.broadcast_to_whiteboard(
            whiteboard_id,
            {
                "type": "user_leave",
                "data": {
                    "userId": user_id,
                    "timestamp": json.loads(json.dumps(str(UUID(user_id))))
                },
                "userId": user_id,
                "timestamp": ""
            },
            exclude_user=user_id
        )
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """
        特定のWebSocketに個人メッセージを送信
        
        Args:
            message: 送信するメッセージ
            websocket: 送信先のWebSocket
        """
        try:
            await websocket.send_text(message)
        except Exception as e:
            print(f"Error sending personal message: {e}")
    
    async def broadcast_to_whiteboard(
        self, 
        whiteboard_id: str, 
        message: dict, 
        exclude_user: str | None = None
    ):
        """
        特定のホワイトボードの全ユーザーにメッセージをブロードキャスト
        
        Args:
            whiteboard_id: ホワイトボードID
            message: 送信するメッセージ
            exclude_user: 除外するユーザーID（送信者など）
        """
        if whiteboard_id not in self.active_connections:
            return
        
        # メッセージをJSON文字列に変換
        message_text = json.dumps(message)
        
        # 切断されたWebSocketを追跡
        disconnected = []
        
        for connection in self.active_connections[whiteboard_id]:
            # 除外ユーザーのチェック
            if exclude_user and connection in self.connection_info:
                user_id, _ = self.connection_info[connection]
                if user_id == exclude_user:
                    continue
            
            try:
                await connection.send_text(message_text)
            except Exception as e:
                print(f"Error broadcasting message: {e}")
                disconnected.append(connection)
        
        # 切断されたWebSocketを削除
        for connection in disconnected:
            if connection in self.connection_info:
                user_id, wb_id = self.connection_info[connection]
                await self.disconnect(connection, wb_id, user_id)
    
    def get_whiteboard_users(self, whiteboard_id: str) -> List[str]:
        """
        特定のホワイトボードに接続しているユーザーIDのリストを取得
        
        Args:
            whiteboard_id: ホワイトボードID
        
        Returns:
            ユーザーIDのリスト
        """
        users = []
        if whiteboard_id in self.active_connections:
            for connection in self.active_connections[whiteboard_id]:
                if connection in self.connection_info:
                    user_id, _ = self.connection_info[connection]
                    if user_id not in users:
                        users.append(user_id)
        return users
    
    def get_user_whiteboards(self, user_id: str) -> Set[str]:
        """
        特定のユーザーが接続しているホワイトボードIDのセットを取得
        
        Args:
            user_id: ユーザーID
        
        Returns:
            ホワイトボードIDのセット
        """
        return self.user_sessions.get(user_id, set())