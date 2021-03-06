"""empty message

Revision ID: deb4de7e9
Revises: 4f87bb7f0ce
Create Date: 2015-02-08 21:29:54.806494

"""

# revision identifiers, used by Alembic.
revision = 'deb4de7e9'
down_revision = '4f87bb7f0ce'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('catalog_item',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('base_image', sa.String(length=255), nullable=True),
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
    sa.Column('group_catalog_id', sa.Integer(), nullable=True),
    sa.Column('coll_status', sa.Integer(), nullable=True),
    sa.Column('image_2', sa.String(length=255), nullable=True),
    sa.ForeignKeyConstraint(['group_catalog_id'], ['group_catalog_item.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('catalog_item')
    ### end Alembic commands ###
