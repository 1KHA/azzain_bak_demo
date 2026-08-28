"""collection_items.gender for made-for-you boards

Revision ID: 92bbdc75b49e
Revises: 341036b0e49a
Create Date: 2026-08-28 15:40:56.451418

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '92bbdc75b49e'
down_revision = '341036b0e49a'
branch_labels = None
depends_on = None


def upgrade():
    # products.image_urls_original is created by prepare_demo.py and is
    # deliberately not on the model; autogenerate proposed dropping it, which
    # would destroy the demo rollback data. Only the board column is applied.
    with op.batch_alter_table('collection_items', schema=None) as batch_op:
        batch_op.add_column(sa.Column('gender', sa.String(length=10), server_default='unisex', nullable=False))

    op.create_index('ix_collection_items_collection_gender', 'collection_items',
                    ['collection_id', 'gender'])


def downgrade():
    op.drop_index('ix_collection_items_collection_gender',
                  table_name='collection_items')

    with op.batch_alter_table('collection_items', schema=None) as batch_op:
        batch_op.drop_column('gender')
