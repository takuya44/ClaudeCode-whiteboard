"""add_tags_and_whiteboard_tags_tables

Revision ID: 93ad320ea3ae
Revises: 5ead97f3b4c3
Create Date: 2025-08-05 13:57:27.472351

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '93ad320ea3ae'
down_revision: Union[str, None] = '5ead97f3b4c3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create tags table
    op.create_table('tags',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('color', sa.String(length=7), nullable=True),
        sa.Column('usage_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_tags_name'), 'tags', ['name'], unique=False)

    # Create whiteboard_tags table
    op.create_table('whiteboard_tags',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('whiteboard_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tag_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['whiteboard_id'], ['whiteboards.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('whiteboard_id', 'tag_id', name='_whiteboard_tag_uc')
    )

    # Create indexes for search performance
    op.create_index('idx_whiteboard_tags', 'whiteboard_tags', ['tag_id'], unique=False)
    op.create_index('idx_whiteboard_tags_whiteboard', 'whiteboard_tags', ['whiteboard_id'], unique=False)
    op.create_index('idx_whiteboard_search', 'whiteboards', ['owner_id', 'created_at', 'updated_at'], unique=False)


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_whiteboard_search', table_name='whiteboards')
    op.drop_index('idx_whiteboard_tags_whiteboard', table_name='whiteboard_tags')
    op.drop_index('idx_whiteboard_tags', table_name='whiteboard_tags')
    
    # Drop tables
    op.drop_table('whiteboard_tags')
    op.drop_index(op.f('ix_tags_name'), table_name='tags')
    op.drop_table('tags')
