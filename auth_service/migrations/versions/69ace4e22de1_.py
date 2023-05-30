"""empty message

Revision ID: 69ace4e22de1
Revises: 6048ce0ac17e
Create Date: 2023-05-30 19:14:52.613242

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '69ace4e22de1'
down_revision = '6048ce0ac17e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('blocklist')
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('lastname',
               existing_type=sa.VARCHAR(length=80),
               nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('lastname',
               existing_type=sa.VARCHAR(length=80),
               nullable=False)

    op.create_table('blocklist',
    sa.Column('token', sa.VARCHAR(length=256), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('token', name='blocklist_pkey')
    )
    # ### end Alembic commands ###