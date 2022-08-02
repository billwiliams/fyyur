"""change column lokking for talent to seekin_talent

Revision ID: 078b5e1aa9e1
Revises: 9ebeb33a46b9
Create Date: 2022-08-02 08:45:13.194057

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '078b5e1aa9e1'
down_revision = '9ebeb33a46b9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Venue', sa.Column('seeking_talent', sa.Boolean(), nullable=False))
    op.drop_column('Venue', 'looking_for_talent')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Venue', sa.Column('looking_for_talent', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.drop_column('Venue', 'seeking_talent')
    # ### end Alembic commands ###
