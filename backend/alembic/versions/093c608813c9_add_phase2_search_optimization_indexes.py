"""Add phase2 search optimization indexes

Revision ID: 093c608813c9
Revises: 93ad320ea3ae
Create Date: 2025-08-08 09:04:53.714200

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '093c608813c9'
down_revision: Union[str, None] = '93ad320ea3ae'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Phase 2: Add advanced search optimization indexes
    
    # 1. GIN index for full-text search on title and description
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_whiteboard_fulltext 
        ON whiteboards 
        USING gin(to_tsvector('english', coalesce(title, '') || ' ' || coalesce(description, '')))
    """)
    
    # 2. Composite index for creator_id + created_at + updated_at (if not exists)
    # This replaces the existing idx_whiteboard_search with better ordering
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_whiteboard_search_composite 
        ON whiteboards (owner_id, created_at DESC, updated_at DESC)
    """)
    
    # 3. Btree index for tag search optimization (replacing GIN as UUID doesn't support GIN)
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_whiteboard_tags_composite 
        ON whiteboard_tags (tag_id, whiteboard_id)
    """)
    
    # 4. Index for permission checks on collaborators
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_collaborators_permission 
        ON whiteboard_collaborators (user_id, whiteboard_id, permission)
    """)
    
    # 5. Index for public whiteboards
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_whiteboards_public 
        ON whiteboards (is_public) 
        WHERE is_public = true
    """)
    
    # 6. Index for tag usage count optimization
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_tags_usage 
        ON tags (usage_count DESC, name)
    """)


def downgrade() -> None:
    # Drop phase 2 optimization indexes
    op.execute("DROP INDEX IF EXISTS idx_whiteboard_fulltext")
    op.execute("DROP INDEX IF EXISTS idx_whiteboard_search_composite")
    op.execute("DROP INDEX IF EXISTS idx_whiteboard_tags_composite")
    op.execute("DROP INDEX IF EXISTS idx_collaborators_permission")
    op.execute("DROP INDEX IF EXISTS idx_whiteboards_public")
    op.execute("DROP INDEX IF EXISTS idx_tags_usage")
