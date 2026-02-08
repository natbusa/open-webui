"""Drop function table

Revision ID: a1b2c3d4e5f6
Revises: 018012973d35
Create Date: 2026-02-08 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa

revision = "a1b2c3d4e5f6"
down_revision = "c440947495f3"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("DROP TABLE IF EXISTS function")


def downgrade():
    # Recreate the function table structure for rollback
    op.create_table(
        "function",
        sa.Column("id", sa.Text(), nullable=False, primary_key=True),
        sa.Column("user_id", sa.Text(), nullable=True),
        sa.Column("name", sa.Text(), nullable=True),
        sa.Column("type", sa.Text(), nullable=True),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("meta", sa.Text(), nullable=True),
        sa.Column("valves", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("is_global", sa.Boolean(), nullable=True),
        sa.Column("updated_at", sa.BigInteger(), nullable=True),
        sa.Column("created_at", sa.BigInteger(), nullable=True),
    )
