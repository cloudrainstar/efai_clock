"""initial migration

Revision ID: 2ee638cfdcb4
Revises: 
Create Date: 2020-12-21 08:29:05.146154

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "2ee638cfdcb4"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "users",
        sa.Column("userid", sa.BigInteger, primary_key=True, nullable=False),
        sa.Column("apollo_user", sa.Text, nullable=False),
        sa.Column("apollo_password", sa.Text, nullable=False),
        sa.Column("reminder", sa.Boolean, nullable=False, default=False),
        sa.Column("autolog", sa.Boolean, nullable=False, default=False),
    )


def downgrade():
    op.drop_table("users")
