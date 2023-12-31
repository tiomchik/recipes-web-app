"""initial migration

Revision ID: 85080ae26b56
Revises: 
Create Date: 2023-11-11 16:10:54.012647

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '85080ae26b56'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('recipes_user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(), nullable=False),
    sa.Column('hashed_password', sa.String(length=1024), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('is_superuser', sa.Boolean(), nullable=False),
    sa.Column('is_verified', sa.Boolean(), nullable=False),
    sa.Column('email', sa.String(length=320), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('username')
    )
    op.create_index(op.f('ix_recipes_user_email'), 'recipes_user', ['email'], unique=True)
    op.create_table('recipe',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('headling', sa.String(length=50), nullable=False),
    sa.Column('text', sa.String(), nullable=False),
    sa.Column('author_id', sa.Integer(), nullable=False),
    sa.CheckConstraint('length(headling) >= 10', name='headling_min_length'),
    sa.CheckConstraint('length(text) >= 10', name='text_min_length'),
    sa.ForeignKeyConstraint(['author_id'], ['recipes_user.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('recipe')
    op.drop_index(op.f('ix_recipes_user_email'), table_name='recipes_user')
    op.drop_table('recipes_user')
    # ### end Alembic commands ###
