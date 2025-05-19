"""Rename longitude column

Revision ID: eca210420234
Revises: e4fecf6f6116
Create Date: 2025-05-19 16:11:22.932126

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'eca210420234'
down_revision: Union[str, None] = 'e4fecf6f6116'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
	op.alter_column('user', 'longtitude', new_column_name='longitude')


def downgrade() -> None:
    op.alter_column('user', 'longitude', new_column_name='longtitude')
