"""empty message

Revision ID: 37830685bc8
Revises: 3a50769880b
Create Date: 2015-01-09 19:56:58.905482

"""

# revision identifiers, used by Alembic.
revision = '37830685bc8'
down_revision = '3a50769880b'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('view_item',
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.PrimaryKeyConstraint('name')
    )
    op.create_table('group_item',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('title')
    )
    op.create_table('group_rights',
    sa.Column('group_id', sa.Integer(), nullable=True),
    sa.Column('view_name', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['group_id'], ['group_item.id'], ),
    sa.ForeignKeyConstraint(['view_name'], ['view_item.name'], )
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('group_rights')
    op.drop_table('group_item')
    op.drop_table('view_item')
    ### end Alembic commands ###