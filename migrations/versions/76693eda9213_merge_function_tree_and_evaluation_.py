"""Merge function tree and evaluation migrations

Revision ID: 76693eda9213
Revises: 1ccffba8ebb0, b3c4d5e6f7a8
Create Date: 2026-09-04 11:02:20.989675

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '76693eda9213'
down_revision = ('1ccffba8ebb0', 'b3c4d5e6f7a8')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
