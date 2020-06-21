"""Add media table

Revision ID: eeefd985259c
Revises: 9ef3c7f40f0f
Create Date: 2020-06-20 21:07:54.887370

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "eeefd985259c"
down_revision = "9ef3c7f40f0f"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "media",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("peripheral_id", sa.Integer(), nullable=False),
        sa.Column("kit_id", sa.Integer(), nullable=False),
        sa.Column("kit_configuration_id", sa.Integer(), nullable=False),
        sa.Column("datetime", sa.DateTime(timezone=True), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("type", sa.String(), nullable=False),
        sa.Column("metadata", postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column("size", sa.BigInteger(), nullable=False),
        sa.CheckConstraint("size >= 0", name="size_positive"),
        sa.ForeignKeyConstraint(
            ["kit_configuration_id"],
            ["kit_configurations.id"],
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["kit_id"], ["kits.id"], onupdate="CASCADE", ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["peripheral_id"],
            ["peripherals.id"],
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_media_datetime"), "media", ["datetime"], unique=False)
    op.create_index(
        op.f("ix_media_kit_configuration_id"),
        "media",
        ["kit_configuration_id"],
        unique=False,
    )
    op.create_index(op.f("ix_media_kit_id"), "media", ["kit_id"], unique=False)
    op.create_index(
        op.f("ix_media_peripheral_id"), "media", ["peripheral_id"], unique=False
    )


def downgrade():
    op.drop_index(op.f("ix_media_peripheral_id"), table_name="media")
    op.drop_index(op.f("ix_media_kit_id"), table_name="media")
    op.drop_index(op.f("ix_media_kit_configuration_id"), table_name="media")
    op.drop_index(op.f("ix_media_datetime"), table_name="media")
    op.drop_table("media")
