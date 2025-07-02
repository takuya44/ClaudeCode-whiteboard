"""Whiteboard management API endpoints."""
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.models.whiteboard import Whiteboard
from app.models.collaborator import WhiteboardCollaborator, Permission
from app.schemas.whiteboard import (
    Whiteboard as WhiteboardSchema,
    WhiteboardCreate,
    WhiteboardUpdate,
    WhiteboardShare,
    WhiteboardPermissionUpdate
)
from app.schemas.user import User as UserSchema

router = APIRouter()


@router.get("/", response_model=List[WhiteboardSchema])
def read_whiteboards(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    現在のユーザーがアクセス可能なホワイトボード一覧を取得
    """
    # 自分が所有するホワイトボード
    owned_whiteboards = db.query(Whiteboard).filter(
        Whiteboard.owner_id == current_user.id
    ).all()

    # 共有されているホワイトボード
    shared_whiteboards = db.query(Whiteboard).join(
        WhiteboardCollaborator
    ).filter(
        WhiteboardCollaborator.user_id == current_user.id
    ).all()

    # 重複を除いて結合
    all_whiteboards = list({wb.id: wb for wb in owned_whiteboards + shared_whiteboards}.values())

    return all_whiteboards[skip : skip + limit]


@router.post("/", response_model=WhiteboardSchema)
def create_whiteboard(
    *,
    db: Session = Depends(get_db),
    whiteboard_in: WhiteboardCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    新しいホワイトボードを作成
    """
    whiteboard = Whiteboard(
        **whiteboard_in.model_dump(),
        owner_id=current_user.id
    )
    db.add(whiteboard)
    db.commit()
    db.refresh(whiteboard)
    return whiteboard


@router.get("/{whiteboard_id}", response_model=WhiteboardSchema)
def read_whiteboard(
    *,
    db: Session = Depends(get_db),
    whiteboard_id: UUID,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    特定のホワイトボードを取得
    """
    whiteboard = db.query(Whiteboard).filter(
        Whiteboard.id == whiteboard_id
    ).first()

    if not whiteboard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Whiteboard not found"
        )

    # アクセス権限チェック
    if not _has_whiteboard_access(db, whiteboard, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    return whiteboard


@router.put("/{whiteboard_id}", response_model=WhiteboardSchema)
def update_whiteboard(
    *,
    db: Session = Depends(get_db),
    whiteboard_id: UUID,
    whiteboard_in: WhiteboardUpdate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    ホワイトボードを更新
    """
    whiteboard = db.query(Whiteboard).filter(
        Whiteboard.id == whiteboard_id
    ).first()

    if not whiteboard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Whiteboard not found"
        )

    # 編集権限チェック
    if not _has_whiteboard_edit_permission(db, whiteboard, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    # 更新
    update_data = whiteboard_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(whiteboard, field, value)

    db.add(whiteboard)
    db.commit()
    db.refresh(whiteboard)
    return whiteboard


@router.delete("/{whiteboard_id}")
def delete_whiteboard(
    *,
    db: Session = Depends(get_db),
    whiteboard_id: UUID,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    ホワイトボードを削除
    """
    whiteboard = db.query(Whiteboard).filter(
        Whiteboard.id == whiteboard_id
    ).first()

    if not whiteboard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Whiteboard not found"
        )

    # 所有者のみ削除可能
    if str(whiteboard.owner_id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owner can delete whiteboard"
        )

    db.delete(whiteboard)
    db.commit()
    return {"detail": "Whiteboard deleted successfully"}


@router.post("/{whiteboard_id}/share")
def share_whiteboard(
    *,
    db: Session = Depends(get_db),
    whiteboard_id: UUID,
    share_request: WhiteboardShare,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    ホワイトボードを他のユーザーと共有
    """
    whiteboard = db.query(Whiteboard).filter(
        Whiteboard.id == whiteboard_id
    ).first()

    if not whiteboard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Whiteboard not found"
        )

    # 管理者権限チェック
    if not _has_whiteboard_admin_permission(db, whiteboard, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owner or admin can share whiteboard"
        )

    # 共有先ユーザーを検索
    user_to_share = db.query(User).filter(
        User.email == share_request.user_email
    ).first()

    if not user_to_share:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # 既に共有されているかチェック
    existing_collaboration = db.query(WhiteboardCollaborator).filter(
        WhiteboardCollaborator.whiteboard_id == whiteboard_id,
        WhiteboardCollaborator.user_id == user_to_share.id
    ).first()

    if existing_collaboration:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already has access to this whiteboard"
        )

    # 共有を作成
    collaboration = WhiteboardCollaborator(
        whiteboard_id=whiteboard_id,
        user_id=user_to_share.id,
        permission=Permission(share_request.permission)
    )
    db.add(collaboration)
    db.commit()

    return {"detail": "Whiteboard shared successfully"}


@router.get("/{whiteboard_id}/users", response_model=List[UserSchema])
def get_whiteboard_users(
    *,
    db: Session = Depends(get_db),
    whiteboard_id: UUID,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    ホワイトボードの参加ユーザー一覧を取得
    """
    whiteboard = db.query(Whiteboard).filter(
        Whiteboard.id == whiteboard_id
    ).first()

    if not whiteboard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Whiteboard not found"
        )

    # アクセス権限チェック
    if not _has_whiteboard_access(db, whiteboard, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    # オーナーを含む全ユーザーを取得
    users = [whiteboard.owner]

    # コラボレーターを追加
    collaborators = db.query(User).join(
        WhiteboardCollaborator
    ).filter(
        WhiteboardCollaborator.whiteboard_id == whiteboard_id
    ).all()

    users.extend(collaborators)

    return users


@router.put("/{whiteboard_id}/permissions")
def update_whiteboard_permissions(
    *,
    db: Session = Depends(get_db),
    whiteboard_id: UUID,
    permission_update: WhiteboardPermissionUpdate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    ホワイトボードの権限を更新
    """
    whiteboard = db.query(Whiteboard).filter(
        Whiteboard.id == whiteboard_id
    ).first()

    if not whiteboard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Whiteboard not found"
        )

    # 管理者権限チェック
    if not _has_whiteboard_admin_permission(db, whiteboard, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owner or admin can update permissions"
        )

    # 対象のコラボレーションを検索
    collaboration = db.query(WhiteboardCollaborator).filter(
        WhiteboardCollaborator.whiteboard_id == whiteboard_id,
        WhiteboardCollaborator.user_id == permission_update.user_id
    ).first()

    if not collaboration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User collaboration not found"
        )

    # 権限を更新
    setattr(collaboration, 'permission', Permission(permission_update.permission))
    db.add(collaboration)
    db.commit()

    return {"detail": "Permission updated successfully"}


# ヘルパー関数

def _has_whiteboard_access(db: Session, whiteboard: Whiteboard, user: User) -> bool:
    """ホワイトボードへのアクセス権限をチェック"""
    if str(whiteboard.owner_id) == str(user.id) or getattr(whiteboard, 'is_public', False):
        return True

    collaboration = db.query(WhiteboardCollaborator).filter(
        WhiteboardCollaborator.whiteboard_id == whiteboard.id,
        WhiteboardCollaborator.user_id == user.id
    ).first()

    return collaboration is not None


def _has_whiteboard_edit_permission(db: Session, whiteboard: Whiteboard, user: User) -> bool:
    """ホワイトボードの編集権限をチェック"""
    if str(whiteboard.owner_id) == str(user.id):
        return True

    collaboration = db.query(WhiteboardCollaborator).filter(
        WhiteboardCollaborator.whiteboard_id == whiteboard.id,
        WhiteboardCollaborator.user_id == user.id
    ).first()

    return collaboration and getattr(collaboration, 'permission', None) in [Permission.EDIT, Permission.ADMIN]


def _has_whiteboard_admin_permission(db: Session, whiteboard: Whiteboard, user: User) -> bool:
    """ホワイトボードの管理者権限をチェック"""
    if str(whiteboard.owner_id) == str(user.id):
        return True

    collaboration = db.query(WhiteboardCollaborator).filter(
        WhiteboardCollaborator.whiteboard_id == whiteboard.id,
        WhiteboardCollaborator.user_id == user.id
    ).first()

    return collaboration and getattr(collaboration, 'permission', None) == Permission.ADMIN
