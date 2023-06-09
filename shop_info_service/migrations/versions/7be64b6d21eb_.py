"""empty message

Revision ID: 7be64b6d21eb
Revises: 5f933480e3cf
Create Date: 2023-06-02 13:36:53.720021

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7be64b6d21eb'
down_revision = '5f933480e3cf'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('shops',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=256), nullable=False),
    sa.Column('legal_entity', sa.String(length=256), nullable=False),
    sa.Column('address', sa.String(length=512), nullable=False),
    sa.Column('owner_id', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('address'),
    sa.UniqueConstraint('owner_id')
    )
    op.drop_table('users')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(length=256), autoincrement=False, nullable=False),
    sa.Column('legal_entity', sa.VARCHAR(length=256), autoincrement=False, nullable=False),
    sa.Column('address', sa.VARCHAR(length=512), autoincrement=False, nullable=False),
    sa.Column('owner_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('current_cash', sa.NUMERIC(), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='users_pkey'),
    sa.UniqueConstraint('address', name='users_address_key'),
    sa.UniqueConstraint('owner_id', name='users_owner_id_key')
    )
    op.drop_table('shops')
    # ### end Alembic commands ###
