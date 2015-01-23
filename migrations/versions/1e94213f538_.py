"""empty message

Revision ID: 1e94213f538
Revises: 2c0e7be024a
Create Date: 2014-12-31 05:35:35.233978

"""

# revision identifiers, used by Alembic.
revision = '1e94213f538'
down_revision = '2c0e7be024a'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('map_item',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('position_x', sa.Float(), nullable=True),
    sa.Column('position_y', sa.Float(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('category_item',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('alias', sa.String(length=255), nullable=True),
    sa.Column('parent_id', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.ForeignKeyConstraint(['parent_id'], ['category_item.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('alias')
    )
    op.create_table('artikul_item',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('alias', sa.String(length=255), nullable=True),
    sa.Column('data', sa.String(), nullable=True),
    sa.Column('category_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['category_id'], ['category_item.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('artikul_item')
    op.drop_table('category_item')
    op.drop_table('map_item')
    ### end Alembic commands ###