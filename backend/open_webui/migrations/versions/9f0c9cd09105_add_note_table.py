"""Add note table

Revision ID: 9f0c9cd09105
Revises: 3781e22d8b01
Create Date: 2025-05-03 03:00:00.000000

"""

from alembic import op
import sqlalchemy as sa

revision = "9f0c9cd09105"
down_revision = "3781e22d8b01"
branch_labels = None
depends_on = None


def upgrade():
    # Note feature removed — table creation is now a no-op.
    pass


def downgrade():
    op.execute("DROP TABLE IF EXISTS note")
