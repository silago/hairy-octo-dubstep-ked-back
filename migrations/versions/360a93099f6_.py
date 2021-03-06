"""empty message

Revision ID: 360a93099f6
Revises: 36d50521263
Create Date: 2014-12-07 22:09:04.562785

"""

# revision identifiers, used by Alembic.
revision = '360a93099f6'
down_revision = '36d50521263'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('page_blocks',
    sa.Column('page_id', sa.Integer(), nullable=True),
    sa.Column('block_id', sa.Integer(), nullable=True),
    sa.Column('place', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['block_id'], ['block_item.id'], ),
    sa.ForeignKeyConstraint(['page_id'], ['page_item.id'], )
    )
    op.drop_table('page_block')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('page_block',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('page_id', sa.INTEGER(), nullable=True),
    sa.Column('block_id', sa.INTEGER(), nullable=True),
    sa.Column('place', sa.VARCHAR(), nullable=True),
    sa.ForeignKeyConstraint(['block_id'], ['block_item.id'], ),
    sa.ForeignKeyConstraint(['page_id'], ['page_item.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('page_blocks')
    ### end Alembic commands ###
