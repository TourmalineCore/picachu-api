"""fix_nullable_hash

Revision ID: 4051e0c243bb
Revises: 2736a57227cf
Create Date: 2022-12-05 08:06:53.461533

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4051e0c243bb'
down_revision = '2736a57227cf'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('photos', 'hash',
               existing_type=sa.VARCHAR(length=2048),
               nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('photos', 'hash',
               existing_type=sa.VARCHAR(length=2048),
               nullable=False)
    # ### end Alembic commands ###
