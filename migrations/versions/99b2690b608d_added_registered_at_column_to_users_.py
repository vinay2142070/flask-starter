"""added registered_at column to users table

Revision ID: 99b2690b608d
Revises: fc840d62152f
Create Date: 2021-09-21 23:45:32.090866

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '99b2690b608d'
down_revision = 'fc840d62152f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('registeredAt', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'registeredAt')
    # ### end Alembic commands ###
