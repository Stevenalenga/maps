"""Initial migration

Revision ID: 6c8c9778acfe
Revises: 
Create Date: 2024-11-02 15:28:44.995538

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6c8c9778acfe'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Use batch mode for SQLite to avoid issues with altering constraints
    with op.batch_alter_table('facts') as batch_op:
        batch_op.create_foreign_key('fk_facts_user_id', 'users', ['user_id'], ['id'])

    with op.batch_alter_table('locations') as batch_op:
        batch_op.alter_column('latitude',
                       existing_type=sa.VARCHAR(),
                       type_=sa.Float(),
                       existing_nullable=False)
        batch_op.alter_column('longitude',
                       existing_type=sa.VARCHAR(),
                       type_=sa.Float(),
                       existing_nullable=False)


def downgrade() -> None:
    # Use batch mode for downgrades as well
    with op.batch_alter_table('locations') as batch_op:
        batch_op.alter_column('longitude',
                       existing_type=sa.Float(),
                       type_=sa.VARCHAR(),
                       existing_nullable=False)
        batch_op.alter_column('latitude',
                       existing_type=sa.Float(),
                       type_=sa.VARCHAR(),
                       existing_nullable=False)

    with op.batch_alter_table('facts') as batch_op:
        batch_op.drop_constraint('fk_facts_user_id', type_='foreignkey')
