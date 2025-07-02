from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# データベースエンジンの作成
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # 接続プールの事前チェック
    echo=settings.is_development  # 開発環境ではSQLログを出力
)

# セッションファクトリーの作成
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# ベースクラスの作成
Base = declarative_base()


# 依存性注入用のデータベースセッション
def get_db():
    """
    FastAPIの依存性注入用関数
    使用例:
        @app.get("/items/")
        def read_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()