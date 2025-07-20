"""Drawing elements API endpoints."""
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.models.whiteboard import Whiteboard, DrawingElement
from app.models.collaborator import WhiteboardCollaborator, Permission
from app.schemas.element import (
    DrawingElement as DrawingElementSchema,
    DrawingElementCreate,
    DrawingElementUpdate,
    BatchElementsUpdate
)

router = APIRouter()


@router.get("/{whiteboard_id}/elements", response_model=List[DrawingElementSchema])
def read_drawing_elements(
    *,
    db: Session = Depends(get_db),
    whiteboard_id: UUID,
    current_user: User = Depends(get_current_active_user),
    skip: int = 0,
    limit: int = 1000,
) -> Any:
    """
    ホワイトボードの描画要素一覧を取得
    """
    # ホワイトボードの存在とアクセス権限をチェック
    _ = _get_whiteboard_with_access_check(db, whiteboard_id, current_user)
    
    elements = db.query(DrawingElement).filter(
        DrawingElement.whiteboard_id == whiteboard_id
    ).order_by(DrawingElement.created_at).all()
    
    return elements[skip : skip + limit]


@router.post("/{whiteboard_id}/elements", response_model=DrawingElementSchema)
def create_drawing_element(
    *,
    db: Session = Depends(get_db),
    whiteboard_id: UUID,
    element_in: DrawingElementCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    新しい描画要素を作成
    """
    # ホワイトボードの存在と編集権限をチェック
    _ = _get_whiteboard_with_edit_check(db, whiteboard_id, current_user)
    
    element = DrawingElement(
        **element_in.model_dump(),
        whiteboard_id=whiteboard_id,
        user_id=current_user.id
    )
    db.add(element)
    db.commit()
    db.refresh(element)
    return element


@router.put("/{whiteboard_id}/elements/{element_id}", response_model=DrawingElementSchema)
def update_drawing_element(
    *,
    db: Session = Depends(get_db),
    whiteboard_id: UUID,
    element_id: UUID,
    element_in: DrawingElementUpdate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    描画要素を更新
    """
    # ホワイトボードの存在と編集権限をチェック
    _ = _get_whiteboard_with_edit_check(db, whiteboard_id, current_user)
    
    element = db.query(DrawingElement).filter(
        DrawingElement.id == element_id,
        DrawingElement.whiteboard_id == whiteboard_id
    ).first()
    
    if not element:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Drawing element not found"
        )
    
    # 更新
    update_data = element_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(element, field, value)
    
    db.add(element)
    db.commit()
    db.refresh(element)
    return element


@router.delete("/{whiteboard_id}/elements/{element_id}")
def delete_drawing_element(
    *,
    db: Session = Depends(get_db),
    whiteboard_id: UUID,
    element_id: UUID,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    描画要素を削除
    """
    # ホワイトボードの存在と編集権限をチェック
    _ = _get_whiteboard_with_edit_check(db, whiteboard_id, current_user)
    
    element = db.query(DrawingElement).filter(
        DrawingElement.id == element_id,
        DrawingElement.whiteboard_id == whiteboard_id
    ).first()
    
    if not element:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Drawing element not found"
        )
    
    db.delete(element)
    db.commit()
    return {"detail": "Drawing element deleted successfully"}


@router.delete("/{whiteboard_id}/elements")
def delete_all_drawing_elements(
    *,
    db: Session = Depends(get_db),
    whiteboard_id: UUID,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    ホワイトボードの全描画要素を削除（クリア機能）
    """
    # ホワイトボードの存在と編集権限をチェック
    _ = _get_whiteboard_with_edit_check(db, whiteboard_id, current_user)
    
    deleted_count = db.query(DrawingElement).filter(
        DrawingElement.whiteboard_id == whiteboard_id
    ).delete()
    
    db.commit()
    return {"detail": f"{deleted_count} drawing elements deleted"}


@router.put("/{whiteboard_id}/elements/batch", response_model=List[DrawingElementSchema])
def save_whiteboard_elements(
    *,
    db: Session = Depends(get_db),
    whiteboard_id: UUID,
    elements_data: BatchElementsUpdate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    ホワイトボードの描画要素を一括保存
    既存の要素をすべて削除して新しい要素で置き換える
    """
    # ホワイトボードの存在と編集権限をチェック
    _ = _get_whiteboard_with_edit_check(db, whiteboard_id, current_user)
    
    # トランザクション内で既存要素の削除と新要素の追加を実行
    try:
        # 既存の要素をすべて削除
        db.query(DrawingElement).filter(
            DrawingElement.whiteboard_id == whiteboard_id
        ).delete()
        
        # 新しい要素を追加
        saved_elements = []
        for element_data in elements_data.elements:
            element = DrawingElement(
                **element_data.model_dump(),
                whiteboard_id=whiteboard_id,
                user_id=current_user.id
            )
            db.add(element)
            saved_elements.append(element)
        
        db.commit()
        
        # 追加された要素を取得してリフレッシュ
        for element in saved_elements:
            db.refresh(element)
        
        return saved_elements
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save whiteboard elements: {str(e)}"
        )


# ヘルパー関数

def _get_whiteboard_with_access_check(
    db: Session, whiteboard_id: UUID, user: User
) -> Whiteboard:
    """ホワイトボードの存在とアクセス権限をチェック"""
    whiteboard = db.query(Whiteboard).filter(
        Whiteboard.id == whiteboard_id
    ).first()
    
    if not whiteboard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Whiteboard not found"
        )
    
    # アクセス権限チェック
    if str(whiteboard.owner_id) != str(user.id) and not getattr(whiteboard, 'is_public', False):
        collaboration = db.query(WhiteboardCollaborator).filter(
            WhiteboardCollaborator.whiteboard_id == whiteboard_id,
            WhiteboardCollaborator.user_id == user.id
        ).first()
        
        if not collaboration:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
    
    return whiteboard


def _get_whiteboard_with_edit_check(
    db: Session, whiteboard_id: UUID, user: User
) -> Whiteboard:
    """ホワイトボードの存在と編集権限をチェック"""
    whiteboard = db.query(Whiteboard).filter(
        Whiteboard.id == whiteboard_id
    ).first()
    
    if not whiteboard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Whiteboard not found"
        )
    
    # 編集権限チェック
    if str(whiteboard.owner_id) != str(user.id):
        collaboration = db.query(WhiteboardCollaborator).filter(
            WhiteboardCollaborator.whiteboard_id == whiteboard_id,
            WhiteboardCollaborator.user_id == user.id
        ).first()
        
        if not collaboration or getattr(collaboration, 'permission', None) == Permission.VIEW:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to edit"
            )
    
    return whiteboard