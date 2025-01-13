"""fresh_start

Revision ID: 1e7a31366cc9
Revises: 
Create Date: 2025-01-13 18:45:11.772355

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1e7a31366cc9'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # First migrate canteen_likes
    op.add_column('canteen_likes', sa.Column('canteen_id_new', sa.String()))
    op.execute("UPDATE canteen_likes SET canteen_id_new = canteen_id::text")
    op.drop_column('canteen_likes', 'canteen_id')
    op.alter_column('canteen_likes', 'canteen_id_new', new_column_name='canteen_id')
    
    # Drop all other tables
    op.drop_table('menu_dish_associations')
    op.drop_table('menu_days')
    op.drop_table('canteen_images')
    op.drop_table('canteen_locations')
    op.drop_table('canteen_opening_hours')
    op.drop_table('canteen_status')
    op.drop_table('canteens')
    
    # Drop the enum type
    op.execute('DROP TYPE canteen_id')
    op.execute('DROP TYPE weekday')
    op.execute('DROP TYPE opening_hours_type')
    

def downgrade() -> None:
    # No downgrade possible as we're deleting data
    pass