"""Add requirement weighting

Revision ID: 8f7b2c1d4e6a
Revises: c24886c3812b
"""
from alembic import op
import sqlalchemy as sa


revision = "8f7b2c1d4e6a"
down_revision = "c24886c3812b"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("requirement", sa.Column("gewichtung_prozent", sa.Float(), nullable=True))
    op.add_column("project", sa.Column("evaluation_comparisons", sa.Text(), nullable=True))


def downgrade():
    op.drop_column("project", "evaluation_comparisons")
    op.drop_column("requirement", "gewichtung_prozent")