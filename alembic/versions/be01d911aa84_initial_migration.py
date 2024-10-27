"""Initial migration

Revision ID: be01d911aa84
Revises: 
Create Date: 2024-xx-xx

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func

# revision identifiers, used by Alembic
revision = 'be01d911aa84'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Create a new table with all the desired columns
    op.execute('''
        CREATE TABLE locations_new (
            id INTEGER PRIMARY KEY,
            name VARCHAR,
            latitude FLOAT,
            longitude FLOAT,
            user_id INTEGER,
            description VARCHAR,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    
    # Copy data from the old table
    op.execute('''
        INSERT INTO locations_new (id, name, latitude, longitude, user_id, description)
        SELECT id, name, latitude, longitude, user_id, description
        FROM locations
    ''')
    
    # Drop the old table
    op.execute('DROP TABLE locations')
    
    # Rename the new table to the original name
    op.execute('ALTER TABLE locations_new RENAME TO locations')
    
    # Recreate indexes
    op.create_index('ix_locations_id', 'locations', ['id'], unique=False)
    op.create_index('ix_locations_name', 'locations', ['name'], unique=False)

def downgrade():
    # Create the original table structure
    op.execute('''
        CREATE TABLE locations_old (
            id INTEGER PRIMARY KEY,
            name VARCHAR,
            latitude FLOAT,
            longitude FLOAT,
            user_id INTEGER,
            description VARCHAR,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    
    # Copy data back, excluding created_at
    op.execute('''
        INSERT INTO locations_old (id, name, latitude, longitude, user_id, description)
        SELECT id, name, latitude, longitude, user_id, description
        FROM locations
    ''')
    
    # Drop the new table
    op.execute('DROP TABLE locations')
    
    # Rename back to original name
    op.execute('ALTER TABLE locations_old RENAME TO locations')
    
    # Recreate original indexes
    op.create_index('ix_locations_id', 'locations', ['id'], unique=False)
    op.create_index('ix_locations_name', 'locations', ['name'], unique=False)