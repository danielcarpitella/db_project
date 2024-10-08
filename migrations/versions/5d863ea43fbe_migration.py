"""migration

Revision ID: 5d863ea43fbe
Revises: 3b58c0be2641
Create Date: 2024-09-24 11:51:52.003736

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5d863ea43fbe'
down_revision = '3b58c0be2641'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('products_cart', schema=None) as batch_op:
        batch_op.add_column(sa.Column('quantity', sa.Integer(), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('products_cart', schema=None) as batch_op:
        batch_op.drop_column('quantity')

    # ### end Alembic commands ###
