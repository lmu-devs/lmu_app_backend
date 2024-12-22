"""add description_short to wishlist translations

Revision ID: fb5ccf089196
Revises: None
Create Date: YYYY-MM-DD HH:MM:SS.SSSSSS

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = 'fb5ccf089196'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # 1. Add column as nullable first
    op.add_column('wishlist_translations', sa.Column('description_short', sa.String(), nullable=True))
    
    # 2. Update existing rows with a default value
    op.execute("UPDATE wishlist_translations SET description_short = description")
    
    # 3. Make the column non-nullable
    op.alter_column('wishlist_translations', 'description_short',
                    existing_type=sa.String(),
                    nullable=False)


def downgrade():
    op.drop_column('wishlist_translations', 'description_short')
