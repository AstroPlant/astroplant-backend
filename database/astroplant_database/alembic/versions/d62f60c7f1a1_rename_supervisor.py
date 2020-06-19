"""Rename supervisor columns.

Revision ID: d62f60c7f1a1
Revises: a3e4ba86f661
Create Date: 2020-06-19 01:48:48.280232

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "d62f60c7f1a1"
down_revision = "a3e4ba86f661"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        "kit_configurations",
        "rules_supervisor_module_name",
        new_column_name="controller_module_name",
    )
    op.alter_column(
        "kit_configurations",
        "rules_supervisor_class_name",
        new_column_name="controller_class_name",
    )
    op.alter_column("kit_configurations", "rules", new_column_name="control_rules")


def downgrade():
    op.alter_column(
        "kit_configurations",
        "controller_module_name",
        new_column_name="rules_supervisor_module_name",
    )
    op.alter_column(
        "kit_configurations",
        "controller_class_name",
        new_column_name="rules_supervisor_class_name",
    )
    op.alter_column("kit_configurations", "control_rules", new_column_name="rules")
