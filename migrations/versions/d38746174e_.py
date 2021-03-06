"""empty message

Revision ID: d38746174e
Revises: 45a96d70d76
Create Date: 2015-01-19 01:37:11.510805

"""

# revision identifiers, used by Alembic.
revision = 'd38746174e'
down_revision = '45a96d70d76'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('catalog_item',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('base_image', sa.String(length=255), nullable=True),
    sa.Column('thumbnail', sa.String(length=255), nullable=True),
    sa.Column('small_image', sa.String(length=255), nullable=True),
    sa.Column('sku', sa.String(length=255), nullable=True),
    sa.Column('color', sa.String(length=255), nullable=True),
    sa.Column('material_top', sa.String(length=255), nullable=True),
    sa.Column('lining', sa.String(length=255), nullable=True),
    sa.Column('analpa_size', sa.String(length=255), nullable=True),
    sa.Column('insole', sa.String(length=255), nullable=True),
    sa.Column('segment', sa.String(length=255), nullable=True),
    sa.Column('season', sa.String(length=255), nullable=True),
    sa.Column('year', sa.String(length=255), nullable=True),
    sa.Column('mark', sa.String(length=255), nullable=True),
    sa.Column('item_type', sa.String(length=255), nullable=True),
    sa.Column('status', sa.String(length=255), nullable=True),
    sa.Column('created_time', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('catalog_item')
    ### end Alembic commands ###
