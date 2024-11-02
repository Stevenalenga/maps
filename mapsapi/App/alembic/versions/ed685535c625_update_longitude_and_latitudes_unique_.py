"""update longitude and latitudes unique constraint

Revision ID: ed685535c625
Revises: e1f36d18da4a
Create Date: 2024-11-02 13:32:16.028317

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic
revision = 'ed685535c625'
down_revision = 'e1f36d18da4a'
branch_labels = None
depends_on = None

def upgrade():
    with op.batch_alter_table("locations") as batch_op:
        batch_op.create_unique_constraint("uq_lat_long", ["latitude", "longitude"])

def downgrade():
    with op.batch_alter_table("locations") as batch_op:
        batch_op.drop_constraint("uq_lat_long", type_="unique")
