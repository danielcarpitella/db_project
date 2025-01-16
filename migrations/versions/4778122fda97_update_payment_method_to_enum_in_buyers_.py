"""Update payment_method to enum in buyers table

Revision ID: 4778122fda97
Revises: 85d8b5e0f9a2
Create Date: 2025-01-16 13:39:37.905735

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '4778122fda97'
down_revision = '85d8b5e0f9a2'
branch_labels = None
depends_on = None


def upgrade():
    # Create the enum type
    payment_method_enum = postgresql.ENUM('Card', 'Paypal', 'Klarna', name='payment_method')
    payment_method_enum.create(op.get_bind())

    # Alter the column to use the new enum type
    with op.batch_alter_table('buyers', schema=None) as batch_op:
        batch_op.alter_column('payment_method',
               existing_type=sa.VARCHAR(),
               type_=payment_method_enum,
               postgresql_using="payment_method::text::payment_method",
               nullable=True)

def downgrade():
    payment_method_enum = postgresql.ENUM('Card', 'Paypal', 'Klarna', name='payment_method')
    payment_method_enum.create(op.get_bind())
    
    # Revert the column to the previous type
    with op.batch_alter_table('buyers', schema=None) as batch_op:
        batch_op.alter_column('payment_method',
               existing_type=payment_method_enum,
               type_=sa.VARCHAR(),
               nullable=False)

    # Drop the enum type
    payment_method_enum.drop(op.get_bind())
