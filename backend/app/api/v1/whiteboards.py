"""Whiteboard management API endpoints."""
from typing import Any, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

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
    WhiteboardPermissionUpdate,
    WhiteboardCollaboratorResponse
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

    # 各ホワイトボードのコラボレーター情報を取得
    result = []
    for wb in all_whiteboards[skip : skip + limit]:
        # コラボレーターの詳細情報を取得
        collaborators = db.query(
            WhiteboardCollaborator.user_id,
            User.name,
            User.email,
            User.role,
            WhiteboardCollaborator.permission,
            User.created_at,
            User.updated_at
        ).join(User).filter(
            WhiteboardCollaborator.whiteboard_id == wb.id
        ).all()
        
        # レスポンス用のコラボレーターデータを構築
        collaborator_responses = []
        for collab in collaborators:
            collaborator_responses.append({
                "user_id": str(collab.user_id),
                "name": collab.name,
                "email": collab.email,
                "role": collab.role,
                "permission": collab.permission.value,
                "created_at": collab.created_at,
                "updated_at": collab.updated_at
            })
        
        # WhiteboardSchemaに合わせてレスポンスを構築
        wb_dict = {
            "id": wb.id,
            "title": wb.title,
            "description": wb.description,
            "is_public": wb.is_public,
            "owner_id": wb.owner_id,
            "created_at": wb.created_at,
            "updated_at": wb.updated_at,
            "owner": wb.owner,
            "collaborators": collaborator_responses
        }
        result.append(wb_dict)

    return result


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

    # コラボレーターの詳細情報を取得
    collaborators = db.query(
        WhiteboardCollaborator.user_id,
        User.name,
        User.email,
        User.role,
        WhiteboardCollaborator.permission,
        User.created_at,
        User.updated_at
    ).join(User).filter(
        WhiteboardCollaborator.whiteboard_id == whiteboard_id
    ).all()
    
    # レスポンス用のコラボレーターデータを構築
    collaborator_responses = []
    for collab in collaborators:
        collaborator_responses.append({
            "user_id": str(collab.user_id),
            "name": collab.name,
            "email": collab.email,
            "role": collab.role,
            "permission": collab.permission.value,
            "created_at": collab.created_at,
            "updated_at": collab.updated_at
        })
    
    # WhiteboardSchemaに合わせてレスポンスを構築
    wb_dict = {
        "id": whiteboard.id,
        "title": whiteboard.title,
        "description": whiteboard.description,
        "is_public": whiteboard.is_public,
        "owner_id": whiteboard.owner_id,
        "created_at": whiteboard.created_at,
        "updated_at": whiteboard.updated_at,
        "owner": whiteboard.owner,
        "collaborators": collaborator_responses
    }

    return wb_dict


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

    shared_users = []
    failed_users = []

    # 複数のユーザーに対して共有処理
    for user_email in share_request.user_emails:
        # 共有先ユーザーを検索
        user_to_share = db.query(User).filter(
            User.email == user_email
        ).first()

        if not user_to_share:
            failed_users.append({
                "email": user_email,
                "error": "User not found"
            })
            continue

        # 既に共有されているかチェック
        existing_collaboration = db.query(WhiteboardCollaborator).filter(
            WhiteboardCollaborator.whiteboard_id == whiteboard_id,
            WhiteboardCollaborator.user_id == user_to_share.id
        ).first()

        if existing_collaboration:
            failed_users.append({
                "email": user_email,
                "error": "User already has access to this whiteboard"
            })
            continue

        # 共有を作成
        collaboration = WhiteboardCollaborator(
            whiteboard_id=whiteboard_id,
            user_id=user_to_share.id,
            permission=Permission(share_request.permission)
        )
        db.add(collaboration)
        shared_users.append({
            "email": user_email,
            "user_id": str(user_to_share.id),
            "permission": share_request.permission
        })

    db.commit()

    # 結果を返す
    if len(shared_users) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No users could be shared",
            headers={"X-Failed-Users": str(failed_users)}
        )

    return {
        "detail": "Whiteboard shared successfully",
        "shared_users": shared_users,
        "failed_users": failed_users
    }


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


@router.get("/{whiteboard_id}/collaborators", response_model=List[WhiteboardCollaboratorResponse])
def get_whiteboard_collaborators(
    *,
    db: Session = Depends(get_db),
    whiteboard_id: UUID,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    ホワイトボードのコラボレーター一覧を取得
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

    # コラボレーター一覧を取得
    collaborators = db.query(
        WhiteboardCollaborator.user_id,
        User.name,
        User.email,
        User.role,
        WhiteboardCollaborator.permission,
        User.created_at,
        User.updated_at
    ).join(User).filter(
        WhiteboardCollaborator.whiteboard_id == whiteboard_id
    ).all()

    # レスポンス形式に変換
    collaborator_responses = []
    for collab in collaborators:
        collaborator_responses.append(WhiteboardCollaboratorResponse(
            user_id=str(collab.user_id),
            name=collab.name,
            email=collab.email,
            role=collab.role,
            permission=collab.permission.value,
            created_at=collab.created_at,
            updated_at=collab.updated_at
        ))

    return collaborator_responses


@router.delete("/{whiteboard_id}/collaborators/{user_id}")
def remove_whiteboard_collaborator(
    *,
    db: Session = Depends(get_db),
    whiteboard_id: UUID,
    user_id: UUID,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    ホワイトボードからコラボレーターを削除
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
            detail="Only owner or admin can remove collaborators"
        )

    # 対象のコラボレーションを検索
    collaboration = db.query(WhiteboardCollaborator).filter(
        WhiteboardCollaborator.whiteboard_id == whiteboard_id,
        WhiteboardCollaborator.user_id == user_id
    ).first()

    if not collaboration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collaborator not found"
        )

    # オーナーは削除できない
    if str(whiteboard.owner_id) == str(user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot remove the owner from collaborators"
        )

    # コラボレーターを削除
    db.delete(collaboration)
    db.commit()

    return {"detail": "Collaborator removed successfully"}


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

    return (collaboration and
            getattr(collaboration, 'permission', None) in [Permission.EDIT,
                                                           Permission.ADMIN])


def _has_whiteboard_admin_permission(db: Session, whiteboard: Whiteboard, user: User) -> bool:
    """ホワイトボードの管理者権限をチェック"""
    if str(whiteboard.owner_id) == str(user.id):
        return True

    collaboration = db.query(WhiteboardCollaborator).filter(
        WhiteboardCollaborator.whiteboard_id == whiteboard.id,
        WhiteboardCollaborator.user_id == user.id
    ).first()

    return (collaboration and
            getattr(collaboration, 'permission', None) == Permission.ADMIN)
