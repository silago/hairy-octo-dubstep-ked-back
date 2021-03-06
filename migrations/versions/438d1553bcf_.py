"""empty message

Revision ID: 438d1553bcf
Revises: 1d618c673
Create Date: 2015-01-19 21:36:01.280494

"""

# revision identifiers, used by Alembic.
revision = '438d1553bcf'
down_revision = '1d618c673'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('catalog_item')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('catalog_item',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('base_image', sa.VARCHAR(length=255), nullable=True),
    sa.Column('thumbnail', sa.VARCHAR(length=255), nullable=True),
    sa.Column('small_image', sa.VARCHAR(length=255), nullable=True),
    sa.Column('sku', sa.VARCHAR(length=255), nullable=True),
    sa.Column('color', sa.VARCHAR(length=255), nullable=True),
    sa.Column('material_top', sa.VARCHAR(length=255), nullable=True),
    sa.Column('lining', sa.VARCHAR(length=255), nullable=True),
    sa.Column('analpa_size', sa.VARCHAR(length=255), nullable=True),
    sa.Column('insole', sa.VARCHAR(length=255), nullable=True),
    sa.Column('segment', sa.VARCHAR(length=255), nullable=True),
    sa.Column('season', sa.VARCHAR(length=255), nullable=True),
    sa.Column('year', sa.VARCHAR(length=255), nullable=True),
    sa.Column('mark', sa.VARCHAR(length=255), nullable=True),
    sa.Column('item_type', sa.VARCHAR(length=255), nullable=True),
    sa.Column('status', sa.VARCHAR(length=255), nullable=True),
    sa.Column('created_time', sa.DATETIME(), nullable=True),
    sa.Column('group_catalog_id', sa.INTEGER(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    ### end Alembic commands ###
