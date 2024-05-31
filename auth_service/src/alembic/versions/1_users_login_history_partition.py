"""users_login_history_partition

Revision ID: 1
Revises:
Create Date: 2024-05-26 10:33:33.909166

"""
from alembic import op

from src.alembic.utils.create_partition import create_partitions, delete_partitions

# revision identifiers, used by Alembic.
revision = "1"
down_revision = "0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    create_partitions(op=op, table_name="users_login_history", months=36)


def downgrade() -> None:
    delete_partitions(op=op, table_name="users_login_history")
