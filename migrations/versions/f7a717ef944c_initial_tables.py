"""initial tables

Revision ID: f7a717ef944c
Revises: 
Create Date: 2021-09-27 08:10:20.596665

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f7a717ef944c'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('player',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('hash', sa.Integer(), nullable=True),
    sa.Column('username', sa.String(length=32), nullable=True),
    sa.Column('rid', sa.String(length=64), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_player_hash'), 'player', ['hash'], unique=True)
    op.create_index(op.f('ix_player_username'), 'player', ['username'], unique=True)
    op.create_table('realm',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=32), nullable=True),
    sa.Column('digest', sa.String(length=64), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_realm_name'), 'realm', ['name'], unique=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_realm_name'), table_name='realm')
    op.drop_table('realm')
    op.drop_index(op.f('ix_player_username'), table_name='player')
    op.drop_index(op.f('ix_player_hash'), table_name='player')
    op.drop_table('player')
    # ### end Alembic commands ###