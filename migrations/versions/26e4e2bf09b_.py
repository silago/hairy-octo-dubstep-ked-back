"""empty message

Revision ID: 26e4e2bf09b
Revises: 26b1c24cddb
Create Date: 2015-01-27 20:47:57.906832

"""

# revision identifiers, used by Alembic.
revision = '26e4e2bf09b'
down_revision = '26b1c24cddb'

from alembic import op
import sqlalchemy as sa


def upgrade():
    pass
    ### commands auto generated by Alembic - please adjust! ###
    ##op.add_column('catalog_item', sa.Column('coll_status', sa.Integer(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    pass
    ### commands auto generated by Alembic - please adjust! ###
    ##op.drop_column('catalog_item', 'coll_status')
    ### end Alembic commands ###