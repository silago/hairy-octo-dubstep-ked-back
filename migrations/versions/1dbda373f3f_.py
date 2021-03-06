"""empty message

Revision ID: 1dbda373f3f
Revises: dc83292a14
Create Date: 2015-01-27 04:02:18.574821

"""

# revision identifiers, used by Alembic.
revision = '1dbda373f3f'
down_revision = 'dc83292a14'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('groups_similar',
    sa.Column('group_id', sa.Integer(), nullable=True),
    sa.Column('similar_group_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['group_id'], ['group_catalog_item.id'], ),
    sa.ForeignKeyConstraint(['similar_group_id'], ['group_catalog_item.id'], )
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('groups_similar')
    ### end Alembic commands ###
