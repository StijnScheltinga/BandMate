"""empty message

Revision ID: 6ecf3b5c0bd1
Revises: e8edcb876000
Create Date: 2025-06-04 13:55:09.998701

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6ecf3b5c0bd1'
down_revision: Union[str, None] = 'e8edcb876000'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('band_invite',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('band_id', sa.Integer(), nullable=True),
    sa.Column('sender_id', sa.Integer(), nullable=True),
    sa.Column('reciever_id', sa.Integer(), nullable=True),
    sa.Column('status', sa.Enum('pending', 'accepted', 'declined', name='status'), nullable=True),
    sa.ForeignKeyConstraint(['band_id'], ['band.id'], ),
    sa.ForeignKeyConstraint(['reciever_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['sender_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('sender_id', 'reciever_id', 'band_id', name='unique_band_invite')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('band_invite')
    # ### end Alembic commands ###
