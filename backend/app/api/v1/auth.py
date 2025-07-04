"""Authentication API endpoints."""
from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core import security
from app.core.config import settings
from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.schemas.auth import Token, Login, PasswordChange
from app.schemas.user import User as UserSchema, UserCreate, UserUpdate

router = APIRouter()


@router.post("/register", response_model=UserSchema)
def register(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate,
) -> Any:
    """
    新規ユーザー登録
    """
    # メールアドレスの重複チェック
    user = db.query(User).filter(User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this email already exists in the system.",
        )

    # 新規ユーザー作成
    user = User(
        email=user_in.email,
        name=user_in.name,
        password_hash=security.get_password_hash(user_in.password),
        avatar=user_in.avatar
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login_json(
    *,
    db: Session = Depends(get_db),
    login_data: Login,
) -> Any:
    """
    JSON形式のログイン（フロントエンド用）
    """
    # ユーザー認証
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user or not security.verify_password(login_data.password, str(user.password_hash)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    # トークン生成
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        subject=str(user.id), expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.post("/login/form", response_model=Token)
def login_form(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2互換のトークンログイン（form-data形式）
    """
    # ユーザー認証
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not security.verify_password(form_data.password, str(user.password_hash)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    # トークン生成
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        subject=str(user.id), expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.post("/logout")
def logout() -> Any:
    """
    ログアウト（クライアント側でトークンを削除）
    """
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserSchema)
def read_users_me(
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    現在のユーザー情報を取得
    """
    return current_user


@router.put("/profile", response_model=UserSchema)
def update_user_profile(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    profile_update: UserUpdate,
) -> Any:
    """
    ユーザープロフィール更新
    """
    # 更新する値のみを設定
    if profile_update.name is not None:
        setattr(current_user, 'name', profile_update.name)
    if profile_update.avatar is not None:
        setattr(current_user, 'avatar', profile_update.avatar)
    if profile_update.password is not None:
        setattr(current_user, 'password_hash', security.get_password_hash(profile_update.password))

    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user


@router.post("/change-password", response_model=dict)
def change_password(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    password_data: PasswordChange,
) -> Any:
    """
    パスワード変更
    """
    # 現在のパスワードを検証
    if not security.verify_password(
        password_data.current_password, str(current_user.password_hash)
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password",
        )

    # 新しいパスワードと現在のパスワードが同じでないことを確認
    if password_data.current_password == password_data.new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from current password",
        )

    # パスワードを更新
    setattr(current_user, 'password_hash', security.get_password_hash(password_data.new_password))
    db.add(current_user)
    db.commit()

    return {"message": "Password changed successfully"}
