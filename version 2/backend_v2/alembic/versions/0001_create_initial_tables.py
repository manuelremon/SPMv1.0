"""create users and solicitudes tables

Revision ID: 0001
Revises: 
Create Date: 2025-11-20
"""
from alembic import op
import sqlalchemy as sa

revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('username', sa.String(100), nullable=False),
        sa.Column('email', sa.String(200), nullable=True),
        sa.Column('full_name', sa.String(200), nullable=True),
        sa.Column('password_hash', sa.String(200), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )
    op.create_table(
        'solicitudes',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('codigo', sa.String(64), nullable=False, index=True),
        sa.Column('centro', sa.String(64), nullable=True),
        sa.Column('codigo_material', sa.String(64), nullable=True),
        sa.Column('cantidad', sa.Integer(), nullable=False, default=0),
        sa.Column('status', sa.String(32), nullable=False, default='pending'),
        sa.Column('priority', sa.String(16), default='normal'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )


def downgrade():
    op.drop_table('solicitudes')
    op.drop_table('users')
