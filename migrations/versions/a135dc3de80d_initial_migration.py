"""Initial migration

Revision ID: a135dc3de80d
Revises: 
Create Date: 2024-08-05 14:41:14.526820

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision = 'a135dc3de80d'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Get the SQLAlchemy connection
    connection = op.get_bind()
    
    # Check if the 'confirmed' column already exists
    inspector = inspect(connection)
    columns = [column['name'] for column in inspector.get_columns('subscription')]
    
    if 'confirmed' not in columns:
        # Only add the column if it doesn't already exist
        with op.batch_alter_table('subscription', schema=None) as batch_op:
            batch_op.add_column(sa.Column('confirmed', sa.Boolean(), nullable=True))
    else:
        print("Column 'confirmed' already exists in 'subscription' table. Skipping.")

# The downgrade() function can remain unchanged