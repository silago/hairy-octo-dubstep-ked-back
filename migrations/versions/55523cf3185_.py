"""empty message

Revision ID: 55523cf3185
Revises: 181233eb63e
Create Date: 2015-02-05 10:53:33.231147

"""

# revision identifiers, used by Alembic.
revision = '55523cf3185'
down_revision = '181233eb63e'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('map_item',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('city_id', sa.Integer(), nullable=True),
    sa.Column('position', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['city_id'], ['city_item.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('map_item')
    ### end Alembic commands ###
