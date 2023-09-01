"""empty message

Revision ID: b1adb7f27779
Revises: 862e20e41f5a
Create Date: 2023-09-01 09:22:13.173713

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b1adb7f27779'
down_revision = '862e20e41f5a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('event', schema=None) as batch_op:
        batch_op.add_column(sa.Column('reading_time', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('number_of_occurrences', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('is_active', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('duration', sa.DateTime(), nullable=True))
        batch_op.drop_column('date_time')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('event', schema=None) as batch_op:
        batch_op.add_column(sa.Column('date_time', sa.DATETIME(), nullable=False))
        batch_op.drop_column('duration')
        batch_op.drop_column('is_active')
        batch_op.drop_column('number_of_occurrences')
        batch_op.drop_column('reading_time')

    # ### end Alembic commands ###