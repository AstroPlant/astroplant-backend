"""Rename module/class to symbol.

Revision ID: 9ef3c7f40f0f
Revises: d62f60c7f1a1
Create Date: 2020-06-19 02:38:03.071893

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "9ef3c7f40f0f"
down_revision = "d62f60c7f1a1"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        "kit_configurations",
        "controller_module_name",
        new_column_name="controller_symbol_location",
    )
    op.alter_column(
        "kit_configurations",
        "controller_class_name",
        new_column_name="controller_symbol",
    )
    op.alter_column(
        "peripheral_definitions",
        "module_name",
        new_column_name="symbol_location",
    )
    op.alter_column(
        "peripheral_definitions",
        "class_name",
        new_column_name="symbol",
    )


def downgrade():
    op.alter_column(
        "kit_configurations",
        "controller_symbol_location",
        new_column_name="controller_module_name",
    )
    op.alter_column(
        "kit_configurations",
        "controller_symbol",
        new_column_name="controller_class_name",
    )
    op.alter_column(
        "peripheral_definitions",
        "symbol_location",
        new_column_name="module_name",
    )
    op.alter_column(
        "peripheral_definitions",
        "symbol",
        new_column_name="class_name",
    )
