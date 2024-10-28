"""complete chatbot model

Revision ID: fab6b96b611d
Revises: accb2a505843
Create Date: 2024-10-28 20:44:10.335509

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = 'fab6b96b611d'
down_revision = 'accb2a505843'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('chatbot',
    sa.Column('title', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
    sa.Column('size', sqlmodel.sql.sqltypes.AutoString(length=50), nullable=False),
    sa.Column('color', sqlmodel.sql.sqltypes.AutoString(length=50), nullable=False),
    sa.Column('logo', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True),
    sa.Column('script', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('owner_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['owner_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('chatbot')
    # ### end Alembic commands ###
