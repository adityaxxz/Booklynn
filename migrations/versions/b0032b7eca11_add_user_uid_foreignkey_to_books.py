"""add user_uid foreignkey to books

Revision ID: b0032b7eca11
Revises: 9e314c2126e7
Create Date: 2025-09-29 13:50:06.802679

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel 


# revision identifiers, used by Alembic.
revision: str = 'b0032b7eca11'
down_revision: Union[str, Sequence[str], None] = '9e314c2126e7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema (SQLite-safe using batch operations)."""
    fk_name = "fk_books_user_uid_user_accounts"
    with op.batch_alter_table('books', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_uid', sa.String(length=36), nullable=True))
        batch_op.create_foreign_key(
            fk_name,
            referent_table='user_accounts',
            local_cols=['user_uid'],
            remote_cols=['uid'],
        )


def downgrade() -> None:
    """Downgrade schema (SQLite-safe using batch operations)."""
    fk_name = "fk_books_user_uid_user_accounts"
    with op.batch_alter_table('books', schema=None) as batch_op:
        batch_op.drop_constraint(fk_name, type_='foreignkey')
        batch_op.drop_column('user_uid')
