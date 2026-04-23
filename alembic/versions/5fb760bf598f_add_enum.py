"""Add enum

Revision ID: 5fb760bf598f
Revises: acbf61612306
Create Date: 2026-04-23 03:15:10.022328
"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "5fb760bf598f"
down_revision: Union[str, Sequence[str], None] = "acbf61612306"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


event_status_enum = postgresql.ENUM(
    "new",
    "published",
    "registration_closed",
    "finished",
    name="event_status_enum",
)

sync_status_enum = postgresql.ENUM(
    "idle",
    "running",
    "success",
    "failed",
    name="sync_status_enum",
)


def upgrade() -> None:
    bind = op.get_bind()

    event_status_enum.create(bind, checkfirst=True)
    sync_status_enum.create(bind, checkfirst=True)

    op.alter_column(
        "events",
        "status",
        existing_type=sa.VARCHAR(length=50),
        type_=event_status_enum,
        existing_nullable=True,
        nullable=False,
        postgresql_using="status::event_status_enum",
    )

    op.alter_column(
        "events",
        "number_of_visitors",
        existing_type=sa.INTEGER(),
        existing_nullable=True,
        nullable=False,
    )

    op.alter_column(
        "places",
        "changed_at",
        existing_type=postgresql.TIMESTAMP(timezone=True),
        existing_server_default=sa.text("now()"),
        existing_nullable=True,
        nullable=False,
    )

    op.alter_column(
        "places",
        "created_at",
        existing_type=postgresql.TIMESTAMP(timezone=True),
        existing_server_default=sa.text("now()"),
        existing_nullable=True,
        nullable=False,
    )

    op.alter_column(
        "sync_state",
        "sync_status",
        existing_type=sa.VARCHAR(length=255),
        type_=sync_status_enum,
        existing_nullable=True,
        nullable=False,
        postgresql_using="sync_status::sync_status_enum",
    )


def downgrade() -> None:
    bind = op.get_bind()

    op.alter_column(
        "sync_state",
        "sync_status",
        existing_type=sync_status_enum,
        type_=sa.VARCHAR(length=255),
        existing_nullable=False,
        nullable=True,
        postgresql_using="sync_status::text",
    )

    op.alter_column(
        "places",
        "created_at",
        existing_type=postgresql.TIMESTAMP(timezone=True),
        existing_server_default=sa.text("now()"),
        existing_nullable=False,
        nullable=True,
    )

    op.alter_column(
        "places",
        "changed_at",
        existing_type=postgresql.TIMESTAMP(timezone=True),
        existing_server_default=sa.text("now()"),
        existing_nullable=False,
        nullable=True,
    )

    op.alter_column(
        "events",
        "number_of_visitors",
        existing_type=sa.INTEGER(),
        existing_nullable=False,
        nullable=True,
    )

    op.alter_column(
        "events",
        "status",
        existing_type=event_status_enum,
        type_=sa.VARCHAR(length=50),
        existing_nullable=False,
        nullable=True,
        postgresql_using="status::text",
    )

    sync_status_enum.drop(bind, checkfirst=True)
    event_status_enum.drop(bind, checkfirst=True)
