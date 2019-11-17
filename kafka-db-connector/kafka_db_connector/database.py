import os
import logging
import datetime
from sqlalchemy import create_engine, event, exc
from sqlalchemy import (
    Column,
    ForeignKey,
    UniqueConstraint,
    PrimaryKeyConstraint,
    CheckConstraint,
)
from sqlalchemy import Integer, Float, String, Text, DateTime, Boolean, DECIMAL
from sqlalchemy import types, Table
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session, relationship


logger = logging.getLogger("astroplant.connector.database")

Base = declarative_base()


# class UTCDateTime(types.TypeDecorator):
#     """
#     Marshall between Python UTC datetime and SQL naive datetime.
#     """
#     impl = types.DateTime

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, timezone=False, **kwargs)

#     def process_bind_param(self, value: datetime.datetime, dialect):
#         if value is not None:
#             assert value.tzinfo is datetime.timezone.utc, (
#                 "Datetimes must be UTC before hitting the database"
#             )

#         return value

#     def process_result_value(self, value: datetime.datetime, dialect):
#         if value is not None:
#             return value.replace(tzinfo=datetime.timezone.utc)
#         else:
#             return value


def utc_now():
    return datetime.datetime.now(tz=datetime.timezone.utc)


class User(Base):
    """
    Model for AstroPlant users.
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(40), unique=True, nullable=False, index=True)
    display_name = Column(String(40), nullable=False)
    password_hash = Column(String(255), nullable=False)
    email_address = Column(String(255), unique=True, nullable=False, index=True)
    use_email_address_for_gravatar = Column(
        Boolean, nullable=False, server_default="true"
    )
    gravatar_alternative = Column(String(255), nullable=False)


class Kit(Base):
    """
    Model for AstroPlant kits.
    """

    __tablename__ = "kits"

    id = Column(Integer, primary_key=True)
    serial = Column(String(20), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    latitude = Column(DECIMAL(11, 8), nullable=True)
    longitude = Column(DECIMAL(11, 8), nullable=True)
    privacy_public_dashboard = Column(Boolean, nullable=False, server_default="false")
    privacy_show_on_map = Column(
        Boolean, nullable=False, server_default="false", index=True
    )


class KitMembership(Base):
    """
    User-Kit memberships.
    """

    __tablename__ = "kit_memberships"

    id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer,
        ForeignKey(User.id, onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    kit_id = Column(
        Integer,
        ForeignKey(Kit.id, onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    datetime_linked = Column(DateTime(timezone=True), nullable=False, default=utc_now)

    access_super = Column(Boolean, nullable=False)
    access_configure = Column(Boolean, nullable=False)

    user = relationship("User", back_populates="kits")
    kit = relationship("Kit", back_populates="users")


User.kits = relationship(
    "KitMembership", order_by=KitMembership.datetime_linked, back_populates="user"
)
Kit.users = relationship(
    "KitMembership", order_by=KitMembership.datetime_linked, back_populates="kit"
)


class KitConfiguration(Base):
    """
    Model of configuration for kits.
    """

    __tablename__ = "kit_configurations"

    id = Column(Integer, primary_key=True)
    kit_id = Column(
        Integer,
        ForeignKey(Kit.id, onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    description = Column(Text, nullable=True)
    rules_supervisor_module_name = Column(Text, nullable=False)
    rules_supervisor_class_name = Column(Text, nullable=False)
    rules = Column(JSON, nullable=False)
    active = Column(Boolean, nullable=False, server_default="false", index=True)
    never_used = Column(Boolean, nullable=False, server_default="true")

    kit = relationship("Kit", back_populates="configurations")

    __table_args__ = (
        CheckConstraint("NOT (active AND never_used)", name="active_and_never_used"),
    )


Kit.configurations = relationship(
    "KitConfiguration", order_by=KitConfiguration.id, back_populates="kit"
)


peripheral_definition_expected_quantity_types = Table(
    "peripheral_definition_expected_quantity_types",
    Base.metadata,
    Column("id", Integer),
    PrimaryKeyConstraint("id"),
    Column(
        "quantity_type_id", Integer, ForeignKey("quantity_types.id"), nullable=False
    ),
    Column(
        "peripheral_definition_id",
        Integer,
        ForeignKey("peripheral_definitions.id"),
        nullable=False,
    ),
)


class QuantityType(Base):
    """
    Model of a quantity type.
    """

    __tablename__ = "quantity_types"

    id = Column(Integer, primary_key=True)
    physical_quantity = Column(String(255), nullable=False)
    physical_unit = Column(String(255), nullable=False)
    physical_unit_symbol = Column(String(255), nullable=True)

    __table_args__ = (UniqueConstraint("physical_quantity", "physical_unit"),)


class PeripheralDefinition(Base):
    """
    Model to hold peripheral device definitions. Each peripheral device of a
    specific type will have its own peripheral device definition.
    """

    __tablename__ = "peripheral_definitions"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    brand = Column(String(100), nullable=True)
    model = Column(String(100), nullable=True)
    module_name = Column(String(255), nullable=False)
    class_name = Column(String(255), nullable=False)

    # A JSON schema http://json-schema.org/.
    configuration_schema = Column(JSON, nullable=False)

    # A JSON schema http://json-schema.org/.
    # If null, the peripheral does not accept commands.
    command_schema = Column(JSON, nullable=True, server_default=None)

    quantity_types = relationship(
        "QuantityType",
        secondary=peripheral_definition_expected_quantity_types,
        backref="peripheral_definitions",
    )


class Peripheral(Base):
    """
    Model of individual peripheral devices. Each such peripheral device belongs
    to a single kit.
    """

    __tablename__ = "peripherals"

    id = Column(Integer, primary_key=True)
    kit_id = Column(
        Integer,
        ForeignKey(Kit.id, onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    kit_configuration_id = Column(
        Integer,
        ForeignKey(KitConfiguration.id, onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    peripheral_definition_id = Column(
        Integer,
        ForeignKey(PeripheralDefinition.id, onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    name = Column(String(255), nullable=False)

    # Must conform to the JSON schema defined by the parent peripheral
    # definition.
    configuration = Column(JSON, nullable=False)

    kit = relationship("Kit", back_populates="peripherals")
    kit_configuration = relationship("KitConfiguration", back_populates="peripherals")
    peripheral_definition = relationship(
        "PeripheralDefinition", back_populates="peripherals"
    )


Kit.peripherals = relationship(
    "Peripheral", order_by=Peripheral.id, back_populates="kit"
)
KitConfiguration.peripherals = relationship(
    "Peripheral", order_by=Peripheral.id, back_populates="kit_configuration"
)
PeripheralDefinition.peripherals = relationship(
    "Peripheral", order_by=Peripheral.id, back_populates="peripheral_definition"
)


class RawMeasurement(Base):
    """
    Model to hold (real-time) raw peripheral device measurements.
    """

    __tablename__ = "raw_measurements"

    id = Column(UUID(as_uuid=True), primary_key=True)
    peripheral_id = Column(
        Integer,
        ForeignKey(Peripheral.id, onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    kit_id = Column(
        Integer,
        ForeignKey(Kit.id, onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    kit_configuration_id = Column(
        Integer,
        ForeignKey(KitConfiguration.id, onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    quantity_type_id = Column(
        Integer,
        ForeignKey(QuantityType.id, onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    value = Column(Float, nullable=False)
    datetime = Column(DateTime(timezone=True), index=True, nullable=False)

    peripheral = relationship("Peripheral", back_populates="raw_measurements")
    kit = relationship("Kit", back_populates="raw_measurements")
    kit_configuration = relationship(
        "KitConfiguration", back_populates="raw_measurements"
    )
    quantity_type = relationship("QuantityType")


class AggregateMeasurement(Base):
    """
    Model to hold aggregate peripheral device measurements.
    """

    __tablename__ = "aggregate_measurements"

    id = Column(UUID(as_uuid=True), primary_key=True)
    peripheral_id = Column(
        Integer,
        ForeignKey(Peripheral.id, onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    kit_id = Column(
        Integer,
        ForeignKey(Kit.id, onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    kit_configuration_id = Column(
        Integer,
        ForeignKey(KitConfiguration.id, onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    quantity_type_id = Column(
        Integer,
        ForeignKey(QuantityType.id, onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    aggregate_type = Column(String(50), nullable=False)
    value = Column(Float, nullable=False)
    datetime_start = Column(DateTime(timezone=True), nullable=False, index=True)
    datetime_end = Column(DateTime(timezone=True), nullable=False, index=True)

    peripheral = relationship("Peripheral", back_populates="aggregate_measurements")
    kit = relationship("Kit", back_populates="aggregate_measurements")
    kit_configuration = relationship(
        "KitConfiguration", back_populates="aggregate_measurements"
    )
    quantity_type = relationship("QuantityType")


Peripheral.raw_measurements = relationship(
    "RawMeasurement", order_by=RawMeasurement.datetime, back_populates="peripheral"
)
Peripheral.aggregate_measurements = relationship(
    "AggregateMeasurement",
    order_by=AggregateMeasurement.datetime_end,
    back_populates="peripheral",
)
Kit.raw_measurements = relationship(
    "RawMeasurement", order_by=RawMeasurement.datetime, back_populates="kit"
)
Kit.aggregate_measurements = relationship(
    "AggregateMeasurement",
    order_by=AggregateMeasurement.datetime_end,
    back_populates="kit",
)
KitConfiguration.raw_measurements = relationship(
    "RawMeasurement",
    order_by=RawMeasurement.datetime,
    back_populates="kit_configuration",
)
KitConfiguration.aggregate_measurements = relationship(
    "AggregateMeasurement",
    order_by=AggregateMeasurement.datetime_end,
    back_populates="kit_configuration",
)


class DatabaseManager(object):
    """
    Provides thread-local scoped database session registry,
    as well as utility functions.
    """

    def __init__(self, host, port, username, password, database):
        self.engine = create_engine(
            (
                "postgresql+psycopg2://"
                f'{username}{":" + password if password else ""}'
                f"@{host}:{port}/{database}"
            ),
            isolation_level="READ COMMITTED",
        )

        # Create new connections in the case the engine is used from a forked
        # process.
        # See: https://docs.sqlalchemy.org/en/latest/core/pooling.html#using-connection-pools-with-multiprocessing
        @event.listens_for(self.engine, "connect")
        def connect(dbapi_connection, connection_record):
            connection_record.info["pid"] = os.getpid()

        @event.listens_for(self.engine, "checkout")
        def checkout(dbapi_connection, connection_record, connection_proxy):
            pid = os.getpid()
            if connection_record.info["pid"] != pid:
                connection_record.connection = connection_proxy.connection = None
                raise exc.DisconnectionError(
                    "Connection record belongs to pid %s, "
                    "attempting to check out in pid %s"
                    % (connection_record.info["pid"], pid)
                )

        session_factory = sessionmaker(bind=self.engine)

        # Thread-local session registry.
        self.Session = scoped_session(session_factory)

    def setup_schema(self):
        Base.metadata.create_all(self.engine)
        self.Session.commit()
        logger.info("New database prepared.")

    def insert_definitions(self, simulation_definitions=False):
        import copy

        qt_temperature = QuantityType(
            physical_quantity="Temperature",
            physical_unit="Degrees Celsius",
            physical_unit_symbol="°C",
        )
        self.Session.add(qt_temperature)

        qt_pressure = QuantityType(
            physical_quantity="Pressure",
            physical_unit="Hectopascal",
            physical_unit_symbol="hPa",
        )
        self.Session.add(qt_pressure)

        qt_humidity = QuantityType(
            physical_quantity="Humidity",
            physical_unit="Percent",
            physical_unit_symbol="%",
        )
        self.Session.add(qt_humidity)

        qt_concentration = QuantityType(
            physical_quantity="Concentration",
            physical_unit="Parts per million",
            physical_unit_symbol="PPM",
        )
        self.Session.add(qt_concentration)

        qt_light_intensity = QuantityType(
            physical_quantity="Light intensity",
            physical_unit="Lux",
            physical_unit_symbol="lx",
        )
        self.Session.add(qt_light_intensity)

        config_measurement_interval = {
            "type": "object",
            "title": "Intervals",
            "required": ["measurementInterval", "aggregateInterval"],
            "properties": {
                "measurementInterval": {
                    "title": "Measurement interval",
                    "description": "The interval in seconds between measurements.",
                    "type": "integer",
                    "minimum": 5,
                    "default": 60,
                },
                "aggregateInterval": {
                    "title": "Aggregate interval",
                    "description": "The interval in seconds between measurement aggregation.",
                    "type": "integer",
                    "minimum": 60,
                    "default": 60 * 30,
                },
            },
        }

        if simulation_definitions:
            # AstroPlant simulation sensors and actuators.
            pd_v_temperature = PeripheralDefinition(
                name="Virtual temperature sensor",
                description=(
                    "A virtual temperature sensor using the environment simulation."
                ),
                brand="AstroPlant Virtual",
                model="Temperature",
                module_name="astroplant_simulation.sensors",
                class_name="Temperature",
                quantity_types=[qt_temperature],
                configuration_schema={
                    "type": "object",
                    "title": "Configuration",
                    "required": ["intervals"],
                    "properties": {"intervals": config_measurement_interval},
                },
            )
            self.Session.add(pd_v_temperature)

            pd_v_pressure = PeripheralDefinition(
                name="Virtual pressure sensor",
                description=(
                    "A virtual pressure sensor using the environment simulation."
                ),
                brand="AstroPlant Virtual",
                model="Pressure",
                module_name="astroplant_simulation.sensors",
                class_name="Pressure",
                quantity_types=[qt_pressure],
                configuration_schema={
                    "type": "object",
                    "title": "Configuration",
                    "required": ["intervals"],
                    "properties": {"intervals": config_measurement_interval},
                },
            )
            self.Session.add(pd_v_pressure)

            pd_v_barometer = PeripheralDefinition(
                name="Virtual barometer",
                description=("A virtual barometer using the environment simulation."),
                brand="AstroPlant Virtual",
                model="Barometer",
                module_name="astroplant_simulation.sensors",
                class_name="Barometer",
                quantity_types=[qt_temperature, qt_pressure, qt_humidity],
                configuration_schema={
                    "type": "object",
                    "title": "Configuration",
                    "required": ["intervals"],
                    "properties": {"intervals": config_measurement_interval},
                },
            )
            self.Session.add(pd_v_barometer)

            pd_v_heater = PeripheralDefinition(
                name="Virtual heater",
                description=("A virtual heater using the environment simulation."),
                brand="AstroPlant Virtual",
                model="Heater",
                module_name="astroplant_simulation.actuators",
                class_name="Heater",
                quantity_types=[],
                configuration_schema={"type": "null", "default": None},
                command_schema={
                    "type": "number",
                    "title": "Heater intensity",
                    "minimum": 0,
                    "maximum": 100,
                },
            )
            self.Session.add(pd_v_heater)

        pd_local_data_logger = PeripheralDefinition(
            name="Local data logger",
            description=("Logs aggregate measurement data locally."),
            brand="AstroPlant",
            model="Logger",
            module_name="peripheral",
            class_name="LocalDataLogger",
            configuration_schema={
                "type": "object",
                "title": "Configuration",
                "required": ["storagePath"],
                "properties": {
                    "storagePath": {
                        "title": "Storage path",
                        "description": "The path to store log files locally. Either absolute, or relative to the program working directory.",
                        "type": "string",
                        "default": "./data",
                    }
                },
            },
        )
        self.Session.add(pd_local_data_logger)

        pd_am2302 = PeripheralDefinition(
            name="AstroPlant air temperature sensor",
            description="Measures air temperature and humidity.",
            brand="Asair",
            model="AM2302",
            quantity_types=[qt_temperature, qt_humidity],
            module_name="astroplant_peripheral_device_library.dht22",
            class_name="Dht22",
            configuration_schema={
                "type": "object",
                "title": "Configuration",
                "required": ["intervals", "gpioAddress"],
                "properties": {
                    "intervals": config_measurement_interval,
                    "gpioAddress": {
                        "title": "GPIO address",
                        "description": "The pin number the sensor is connected to.",
                        "type": "integer",
                        "default": 17,
                    },
                },
            },
        )
        self.Session.add(pd_am2302)

        pd_mh_z19 = PeripheralDefinition(
            name="AstroPlant air CO² sensor",
            description="Measures carbon dioxide concentration in the air.",
            brand=None,
            model="MH-Z19",
            quantity_types=[qt_concentration],
            module_name="astroplant_peripheral_device_library.mh_z19",
            class_name="MhZ19",
            configuration_schema={
                "type": "object",
                "title": "Configuration",
                "required": ["intervals", "serialDeviceFile"],
                "properties": {
                    "intervals": config_measurement_interval,
                    "serialDeviceFile": {
                        "title": "Serial device",
                        "description": "The device file name of the serial interface.",
                        "type": "string",
                        "default": "/dev/ttyS0",
                    },
                },
            },
        )
        self.Session.add(pd_mh_z19)

        pd_bh1750 = PeripheralDefinition(
            name="AstroPlant light sensor",
            description="Measures light intensity.",
            brand=None,
            model="BH1750",
            quantity_types=[qt_light_intensity],
            module_name="astroplant_peripheral_device_library.bh1750",
            class_name="Bh1750",
            configuration_schema={
                "type": "object",
                "title": "Configuration",
                "required": ["intervals", "i2cAddress"],
                "properties": {
                    "intervals": config_measurement_interval,
                    "i2cAddress": {
                        "title": "I2C address",
                        "description": "The I2C address of this device.",
                        "type": "string",
                        "default": "0x23",
                    },
                },
            },
        )
        self.Session.add(pd_bh1750)

        pd_ds18b20 = PeripheralDefinition(
            name="AstroPlant water temperature sensor",
            description="Measures water temperature.",
            brand=None,
            model="DS18B20",
            quantity_types=[qt_temperature],
            module_name="astroplant_peripheral_device_library.ds18b20",
            class_name="Ds18b20",
            configuration_schema={
                "type": "object",
                "title": "Configuration",
                "required": ["intervals"],
                "properties": {
                    "intervals": config_measurement_interval,
                    "oneWireDeviceId": {
                        "type": "string",
                        "title": "1-Wire device identifier",
                        "description": "The 1-Wire device ID to filter on. Keep blank to not filter on device IDs.",
                    },
                },
            },
        )
        self.Session.add(pd_ds18b20)

        pd_fans = PeripheralDefinition(
            name="AstroPlant fans",
            description="AstroPlant fans controlled through PWM.",
            brand=None,
            model="24V DC",
            module_name="astroplant_peripheral_device_library.pwm",
            class_name="Pwm",
            configuration_schema={
                "type": "object",
                "title": "Configuration",
                "required": ["gpioAddresses"],
                "properties": {
                    "gpioAddresses": {
                        "title": "GPIO addresses",
                        "description": "The GPIO addresses this logical fan device controls.",
                        "type": "array",
                        "items": {"type": "integer"},
                        "default": [16, 19],
                    }
                },
            },
            command_schema={
                "type": "number",
                "title": "Fan intensity",
                "description": "The fan intensity as a percentage of full power.",
                "minimum": 0,
                "maximum": 100,
            },
        )
        self.Session.add(pd_fans)

        pd_led_panel = PeripheralDefinition(
            name="AstroPlant LED panel",
            description="AstroPlant led panel controlled through PWM.",
            brand="AstroPlant",
            model="mk06",
            module_name="astroplant_peripheral_device_library.led_panel",
            class_name="LedPanel",
            configuration_schema={
                "type": "object",
                "title": "Configuration",
                "required": ["gpioAddressBlue", "gpioAddressRed", "gpioAddressFarRed"],
                "properties": {
                    "gpioAddressBlue": {
                        "title": "GPIO address blue",
                        "description": "The GPIO address for PWM control of the blue LED.",
                        "type": "integer",
                        "default": 21,
                    },
                    "gpioAddressRed": {
                        "title": "GPIO address red",
                        "description": "The GPIO address for PWM control of the red LED.",
                        "type": "integer",
                        "default": 20,
                    },
                    "gpioAddressFarRed": {
                        "title": "GPIO address far-red",
                        "description": "The GPIO address for PWM control of the far-red LED.",
                        "type": "integer",
                        "default": 18,
                    },
                },
            },
            command_schema={
                "type": "object",
                "title": "LED brightness",
                "description": "The LED brightnesses as percentage of full brightness.",
                "required": [],
                "properties": {
                    "blue": {"type": "integer", "minimum": 0, "maximum": 100},
                    "red": {"type": "integer", "minimum": 0, "maximum": 100},
                    "farRed": {"type": "integer", "minimum": 0, "maximum": 100},
                },
            },
        )
        self.Session.add(pd_led_panel)

        self.Session.commit()
