"""
First migration script.

Revision ID: 3057e681742b
Revises:
Create Date: 2025-08-28 08:09:22.248848

"""
from __future__ import annotations

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "3057e681742b"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # ! WARNING: The SQL needs to be compatible with all supported databases: PostgreSQL and SQLite.
    op.execute("select current_timestamp;")


def downgrade() -> None:
    """Downgrade schema."""
