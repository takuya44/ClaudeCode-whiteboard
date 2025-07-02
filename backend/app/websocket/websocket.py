from fastapi import WebSocket, WebSocketDisconnect, status
from jose import jwt, JWTError
from uuid import UUID
import json

from app.core.database import get_db
from app.core import security
from app.core.config import settings
from app.models.user import User
from app.models.whiteboard import Whiteboard
from app.models.collaborator import WhiteboardCollaborator
from app.websocket.connection_manager import ConnectionManager
from app.websocket.message_handler import MessageHandler

# グローバル接続マネージャー
manager = ConnectionManager()
message_handler = MessageHandler(manager)


async def websocket_endpoint(
    websocket: WebSocket,
    whiteboard_id: str,
    user_id: str | None = None,
    token: str | None = None
):
    """
    WebSocketエンドポイント
    
    Args:
        websocket: WebSocket接続
        whiteboard_id: ホワイトボードID
        user_id: ユーザーID（クエリパラメータ）
        token: JWTトークン（クエリパラメータ）
    """
    # データベースセッションを取得
    db_generator = get_db()
    db = next(db_generator)
    
    try:
        # 認証チェック
        if not token or not user_id:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        
        # JWTトークンの検証
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[security.ALGORITHM])
            token_user_id = payload.get("sub")
            if token_user_id != user_id:
                await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
                return
        except JWTError:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        
        # ユーザーの存在確認
        user = db.query(User).filter(User.id == UUID(user_id)).first()
        if not user:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        
        # ホワイトボードの存在確認
        whiteboard = db.query(Whiteboard).filter(
            Whiteboard.id == UUID(whiteboard_id)
        ).first()
        if not whiteboard:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        
        # アクセス権限の確認
        has_access = False
        user_uuid = UUID(user_id)
        if str(whiteboard.owner_id) == user_id:
            has_access = True
        elif bool(getattr(whiteboard, 'is_public', False)):
            has_access = True
        else:
            collaboration = db.query(WhiteboardCollaborator).filter(
                WhiteboardCollaborator.whiteboard_id == UUID(whiteboard_id),
                WhiteboardCollaborator.user_id == user_uuid
            ).first()
            if collaboration:
                has_access = True
        
        if not has_access:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        
        # 接続を受け入れ
        await manager.connect(websocket, whiteboard_id, user_id)
        
        # メッセージ受信ループ
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # メッセージを処理
                await message_handler.handle_message(
                    message, whiteboard_id, user_id, db
                )
                
            except WebSocketDisconnect:
                break
            except json.JSONDecodeError:
                print("Invalid JSON received")
            except Exception as e:
                print(f"Error processing message: {e}")
    
    except Exception as e:
        print(f"WebSocket error: {e}")
        try:
            await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
        except:
            pass
    
    finally:
        # 切断処理
        if user_id:
            await manager.disconnect(websocket, whiteboard_id, user_id)
        # データベースセッションをクローズ
        try:
            db.close()
        except:
            pass


def get_connection_manager() -> ConnectionManager:
    """接続マネージャーを取得"""
    return manager


def get_message_handler() -> MessageHandler:
    """メッセージハンドラーを取得"""
    return message_handler