"""Collapse aggregates.

Revision ID: a3e4ba86f661
Revises: 
Create Date: 2020-06-05 22:54:47.996913

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import orm, Column, Integer, Float, String, DateTime
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.declarative import declarative_base

# revision identifiers, used by Alembic.
revision = "a3e4ba86f661"
down_revision = None
branch_labels = None
depends_on = None

Base = declarative_base()


class AggregateMeasurement(Base):
    __tablename__ = "aggregate_measurements"

    id = Column(postgresql.UUID(as_uuid=True), primary_key=True)
    peripheral_id = Column(Integer, nullable=False, index=True,)
    kit_id = Column(Integer, nullable=False, index=True,)
    kit_configuration_id = Column(Integer, nullable=False, index=True,)
    quantity_type_id = Column(Integer, nullable=False, index=True,)
    datetime_start = Column(DateTime(timezone=True), nullable=False, index=True)
    datetime_end = Column(DateTime(timezone=True), nullable=False, index=True)
    values = Column(postgresql.JSON, nullable=True)
    aggregate_type = Column(String(50), nullable=False)
    value = Column(Float, nullable=False)


def upgrade():
    bind = op.get_bind()
    session = orm.Session(bind=bind)

    op.add_column(
        "aggregate_measurements",
        sa.Column("values", postgresql.JSON(astext_type=sa.Text()), nullable=True),
    )

    # Migrate data (collapse aggregates into single rows).
    first_of_group = None
    values = {}
    for measurement in (
        session.query(AggregateMeasurement)
        .order_by(
            AggregateMeasurement.peripheral_id.asc(),
            AggregateMeasurement.quantity_type_id.asc(),
            AggregateMeasurement.datetime_start.asc(),
        )
        .yield_per(100)
    ):
        if (
            first_of_group is None
            or first_of_group.peripheral_id != measurement.peripheral_id
            or first_of_group.quantity_type_id != measurement.quantity_type_id
            or first_of_group.datetime_start != measurement.datetime_start
        ):
            if first_of_group is not None:
                # End of group.
                first_of_group.values = values
            first_of_group = measurement
            values = {}
        values[measurement.aggregate_type] = measurement.value

    if first_of_group is not None:
        first_of_group.values = values
    session.query(AggregateMeasurement).filter(
        AggregateMeasurement.values == None
    ).delete()
    session.commit()

    op.alter_column("aggregate_measurements", "values", nullable=False)

    op.create_index(
        "ix_aggregate_measurements_datetime_start_id",
        "aggregate_measurements",
        ["datetime_start", "id"],
        unique=False,
    )
    op.drop_index(
        "ix_aggregate_measurements_datetime_end", table_name="aggregate_measurements"
    )
    op.drop_column("aggregate_measurements", "aggregate_type")
    op.drop_column("aggregate_measurements", "value")
