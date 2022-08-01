"""Add Columns to Artist Model

Revision ID: 9fbdbb3e3ad3
Revises: 5be30ce03d89
Create Date: 2022-08-01 11:15:22.467737

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9fbdbb3e3ad3'
down_revision = '5be30ce03d89'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Artist', sa.Column('website_link', sa.String(length=120), nullable=True))
    op.add_column('Artist', sa.Column('looking_for_venues', sa.Boolean(), nullable=True))
    op.add_column('Artist', sa.Column('seeking_description', sa.String(length=500), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Artist', 'seeking_description')
    op.drop_column('Artist', 'looking_for_venues')
    op.drop_column('Artist', 'website_link')
    # ### end Alembic commands ###
