"""Store the last requirement comparison matrix

Revision ID: b3c4d5e6f7a8
Revises: 8f7b2c1d4e6a
"""
from alembic import op
import sqlalchemy as sa


revision = "b3c4d5e6f7a8"
down_revision = "8f7b2c1d4e6a"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("project", sa.Column("evaluation_comparisons", sa.Text(), nullable=True))


def downgrade():
    op.drop_column("project", "evaluation_comparisons")