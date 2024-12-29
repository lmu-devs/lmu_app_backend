"""add blurhash to canteen images

Revision ID: c6502cecec69
Revises: fb5ccf089196
Create Date: 2024-12-28 23:45:52.054926

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c6502cecec69'
down_revision: Union[str, None] = 'fb5ccf089196'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('canteen_images', sa.Column('blurhash', sa.String(), nullable=True))
    op.add_column('wishlist_images', sa.Column('blurhash', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('canteen_images', 'blurhash')
    op.drop_column('wishlist_images', 'blurhash')
