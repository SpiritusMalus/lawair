"""add is_active to users

Revision ID: a1b2c3d4e5f6
Revises: 6821c3514ea8
Create Date: 2026-04-18 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision: str = 'a1b2c3d4e5f6'
down_revision: str = '6821c3514ea8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('users', sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()))


def downgrade() -> None:
    op.drop_column('users', 'is_active')
