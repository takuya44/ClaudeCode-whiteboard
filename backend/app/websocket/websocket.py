from fastapi import WebSocket, WebSocketDisconnect, status
import json

from app.core.database import get_db
from app.websocket.connection_manager import ConnectionManager
from app.websocket.message_handler import MessageHandler

# グローバル接続マネージャー
manager = ConnectionManager()
message_handler = MessageHandler(manager)


async def websocket_endpoint(
    websocket: WebSocket,
    whiteboard_id: str
):
    """
    WebSocketエンドポイント
    
    Args:
        websocket: WebSocket接続
        whiteboard_id: ホワイトボードID
    
    クエリパラメータ:
        userId: ユーザーID
        token: JWTトークン
    """
    # データベースセッションを取得
    db_generator = get_db()
    db = next(db_generator)
    
    try:
        # WebSocketクエリパラメータを手動で解析
        query_params = websocket.query_params
        user_id_param = query_params.get('userId')
        token = query_params.get('token')
        
        print(f"WebSocket connection attempt: whiteboard_id={whiteboard_id}, user_id={user_id_param}, token={token[:50] if token else None}...")
        print(f"Query params - user_id type: {type(user_id_param)}, token type: {type(token)}")
        
        # user_idの型チェックとバリデーション
        if not user_id_param:
            print("Error: user_id is required")
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        
        # str型に変換
        user_id_str = str(user_id_param)
        
        print(f"WebSocket accepted for user {user_id_str} on whiteboard {whiteboard_id}")
        
        # 接続マネージャーを使用して接続を管理
        await manager.connect(websocket, whiteboard_id, user_id_str)
        
        # 簡単なテストメッセージを送信
        test_message = {
            "type": "connection_success",
            "data": {"message": "Connected successfully"},
            "userId": user_id_str,
            "timestamp": ""
        }
        await websocket.send_text(json.dumps(test_message))
        
        # 接続を維持
        try:
            while True:
                data = await websocket.receive_text()
                message = json.loads(data)
                print(f"Received message: {message}")
                
                # メッセージハンドラーで処理
                await message_handler.handle_message(message, whiteboard_id, user_id_str, db)
                
        except WebSocketDisconnect:
            print(f"WebSocket disconnected for user {user_id_str} on whiteboard {whiteboard_id}")
        except Exception as e:
            print(f"Message handling error: {e}")
            # WebSocket接続を終了
        finally:
            # 接続マネージャーから切断
            await manager.disconnect(websocket, whiteboard_id, user_id_str)
        
        return
    
    except Exception as e:
        print(f"WebSocket error: {e}")
        try:
            await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
        except Exception as close_error:
            print(f"Error closing WebSocket: {close_error}")
    
    finally:
        # 切断処理
        try:
            # user_id_strが定義されている場合のみ切断処理
            if 'user_id_str' in locals():
                await manager.disconnect(websocket, whiteboard_id, user_id_str)
        except Exception as e:
            print(f"Error during disconnect: {e}")
        
        # データベースセッションをクローズ
        try:
            if hasattr(db, 'close'):
                db.close()
        except Exception as db_error:
            print(f"Error closing database session: {db_error}")


def get_connection_manager() -> ConnectionManager:
    """接続マネージャーを取得"""
    return manager


def get_message_handler() -> MessageHandler:
    """メッセージハンドラーを取得"""
    return message_handler