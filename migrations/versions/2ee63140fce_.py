"""empty message

Revision ID: 2ee63140fce
Revises: d7f7536a65
Create Date: 2014-12-15 01:52:14.826218

"""

# revision identifiers, used by Alembic.
revision = '2ee63140fce'
down_revision = 'd7f7536a65'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user_item',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(), nullable=True),
    sa.Column('password', sa.String(), nullable=True),
    sa.Column('role_id', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('username')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_item')
    ### end Alembic commands ###
