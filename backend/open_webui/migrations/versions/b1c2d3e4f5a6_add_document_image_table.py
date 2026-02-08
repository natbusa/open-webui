"""Add document_image table

Revision ID: b1c2d3e4f5a6
Revises: a1b2c3d4e5f6
Create Date: 2026-02-08 12:00:00.000000

"""

from alembic import op
import sqlalchemy as sa

revision = "b1c2d3e4f5a6"
down_revision = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "document_image",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("file_id", sa.String(), nullable=False),
        sa.Column("image_file_id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("created_at", sa.BigInteger()),
        sa.Column("updated_at", sa.BigInteger()),
        sa.UniqueConstraint("file_id", "image_file_id", name="uq_file_image"),
    )
    op.create_index("ix_document_image_file_id", "document_image", ["file_id"])
    op.create_index(
        "ix_document_image_image_file_id", "document_image", ["image_file_id"]
    )
    op.create_index("ix_document_image_user_id", "document_image", ["user_id"])


def downgrade():
    op.drop_index("ix_document_image_user_id", table_name="document_image")
    op.drop_index("ix_document_image_image_file_id", table_name="document_image")
    op.drop_index("ix_document_image_file_id", table_name="document_image")
    op.drop_table("document_image")
