"""add_canteen_type_enum

Revision ID: 7faab058e3fe
Revises: 
Create Date: 2024-10-30 19:54:28.129774

"""
from typing import Sequence, Union

from api.models.canteen_model.py import CanteenType
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7faab058e3fe'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Create a temporary table with the new column
    with op.batch_alter_table('canteens') as batch_op:
        # Create the enum type and column in one step
        batch_op.add_column(
            sa.Column('type',
                     sa.Enum(CanteenType, 
                            name='canteen_type',
                            create_type=True,  # This will create the type if it doesn't exist
                            native_enum=True),
                     nullable=True)
        )

def downgrade():
    with op.batch_alter_table('canteens') as batch_op:
        batch_op.drop_column('type')
    
    # Drop the enum type
    canteen_type = sa.Enum(name='canteen_type')
    canteen_type.drop(op.get_bind(), checkfirst=True)
