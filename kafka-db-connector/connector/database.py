import os
import logging
import datetime
from sqlalchemy import create_engine, event, exc
from sqlalchemy import Column, ForeignKey, UniqueConstraint
from sqlalchemy import Integer, Float, String, Text, DateTime, Boolean, DECIMAL
from sqlalchemy import types, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session, relationship


logger = logging.getLogger('astroplant.connector')

Base = declarative_base()


class UTCDateTime(types.TypeDecorator):
    """
    Marshall between Python UTC datetime and SQL naive datetime.
    """
    impl = types.DateTime

    def __init__(self, *args, **kwargs):
        super().__init__(*args, timezone=False, **kwargs)

    def process_bind_param(self, value: datetime.datetime, dialect):
        if value is not None:
            assert value.tzinfo is datetime.timezone.utc, (
                "Datetimes must be UTC before hitting the database"
            )

        return value

    def process_result_value(self, value: datetime.datetime, dialect):
        if value is not None:
            return value.replace(tzinfo=datetime.timezone.utc)
        else:
            return value


class User(Base):
    """
    Model for AstroPlant users.
    """
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(40), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    email_address = Column(String(255), unique=True, nullable=False, index=True)
    use_gravatar = Column(Boolean, nullable=False, default=True)
    gravatar_alternative = Column(String(255), nullable=False)


class Kit(Base):
    """
    Model for AstroPlant kits.
    """
    __tablename__ = 'kits'

    id = Column(Integer, primary_key=True)
    serial = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    latitude = Column(DECIMAL(11, 8), nullable=True)
    longitude = Column(DECIMAL(11, 8), nullable=True)
    privacy_public_dashboard = Column(Boolean, nullable=False, default=False)
    privacy_show_on_map = Column(
        Boolean,
        nullable=False,
        default=False,
        index=True,
    )


class KitMembership(Base):
    """
    User-Kit memberships.
    """
    __tablename__ = 'kit_memberships'

    id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer,
        ForeignKey(User.id, onupdate='CASCADE', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    kit_id = Column(
        Integer,
        ForeignKey(Kit.id, onupdate='CASCADE', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    datetime_linked = Column(UTCDateTime, nullable=False)

    user = relationship('User', back_populates='kits')
    kit = relationship('Kit', back_populates='users')


User.kits = relationship(
    'KitMembership',
    order_by=KitMembership.datetime_linked,
    back_populates='user',
)
Kit.users = relationship(
    'KitMembership',
    order_by=KitMembership.datetime_linked,
    back_populates='kit',
)


peripheral_definition_expected_quantity_types = Table(
    'peripheral_definition_expected_quantity_type',
    Base.metadata,
    Column(
        'quantity_type_id',
        Integer,
        ForeignKey('quantity_types.id'),
    ),
    Column(
        'peripheral_definition_id',
        Integer,
        ForeignKey('peripheral_definitions.id'),
    ),
)


class QuantityType(Base):
    """
    Model of a quantity type.
    """
    __tablename__ = 'quantity_types'

    id = Column(Integer, primary_key=True)
    physical_quantity = Column(String(255), nullable=False)
    physical_unit = Column(String(255), nullable=False)
    physical_unit_symbol = Column(String(255), nullable=True)

    __table_args__ = (
        UniqueConstraint('physical_quantity', 'physical_unit'),
    )


class PeripheralDefinition(Base):
    """
    Model to hold peripheral device definitions. Each peripheral device of a
    specific type will have its own peripheral device definition.
    """
    __tablename__ = 'peripheral_definitions'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    brand = Column(String(100), nullable=True)
    model = Column(String(100), nullable=True)
    module_name = Column(String(255), nullable=False)
    class_name = Column(String(255), nullable=False)
    quantity_types = relationship(
        'QuantityType',
        secondary=peripheral_definition_expected_quantity_types,
        backref='peripheral_definitions'
    )


class PeripheralConfigurationDefinition(Base):
    """
    Model to hold the definitions for configuration options of peripheral
    devices.
    """
    __tablename__ = 'peripheral_configuration_definitions'

    id = Column(Integer, primary_key=True)
    peripheral_definition_id = Column(
        Integer,
        ForeignKey(
            PeripheralDefinition.id,
            onupdate='CASCADE',
            ondelete='CASCADE',
            ),
        nullable=False,
    )
    name = Column(String(100), nullable=False)
    default_value = Column(Text, nullable=True)
    description = Column(Text)

    peripheral_definition = relationship(
        'PeripheralDefinition',
        back_populates='configuration_definitions',
    )

    __table_args__ = (
        UniqueConstraint('peripheral_definition_id', 'name'),
    )


PeripheralDefinition.configuration_definitions = relationship(
    'PeripheralConfigurationDefinition',
    order_by=PeripheralConfigurationDefinition.id,
    back_populates='peripheral_definition',
)


class Peripheral(Base):
    """
    Model of individual peripheral devices. Each such peripheral device belongs
    to a single kit.
    """
    __tablename__ = 'peripherals'

    id = Column(Integer, primary_key=True)
    kit_id = Column(
        Integer,
        ForeignKey(Kit.id, onupdate='CASCADE', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    peripheral_definition_id = Column(
        Integer,
        ForeignKey(
            PeripheralDefinition.id,
            onupdate='CASCADE',
            ondelete='CASCADE',
        ),
        nullable=False,
    )
    name = Column(String(255), nullable=False)
    active = Column(Boolean, nullable=False, default=True)
    added_datetime = Column(UTCDateTime)
    removed_datetime = Column(UTCDateTime)

    peripheral_definition = relationship(
        'PeripheralDefinition',
        back_populates='peripherals',
    )


PeripheralDefinition.peripherals = relationship(
    'Peripheral',
    order_by=Peripheral.id,
    back_populates='peripheral_definition',
)


class PeripheralConfiguration(Base):
    """
    Model of configuration for individual peripheral devices.
    """
    __tablename__ = 'peripheral_configurations'

    id = Column(Integer, primary_key=True)
    peripheral_id = Column(
        Integer,
        ForeignKey(
            Peripheral.id,
            onupdate='CASCADE',
            ondelete='CASCADE',
        ),
        nullable=False,
    )
    peripheral_configuration_definition_id = Column(
        Integer,
        ForeignKey(
            PeripheralConfigurationDefinition.id,
            onupdate='CASCADE',
            ondelete='CASCADE',
        ),
        nullable=False,
    )
    value = Column(Text, nullable=True)

    peripheral = relationship(
        'Peripheral',
        back_populates='configurations',
    )
    configuration_definition = relationship(
        'PeripheralConfigurationDefinition',
    )

    __table_args__ = (
        UniqueConstraint(
            'peripheral_id',
            'peripheral_configuration_definition_id',
        ),
    )


Peripheral.configurations = relationship(
    'PeripheralConfiguration',
    order_by=PeripheralConfiguration.id,
    back_populates='peripheral',
)


class Measurement(Base):
    """
    Model to hold peripheral device measurements.
    """
    __tablename__ = 'measurements'

    id = Column(Integer, primary_key=True)
    peripheral_id = Column(
        Integer,
        ForeignKey(Peripheral.id, onupdate='CASCADE', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    kit_id = Column(
        Integer,
        ForeignKey(Kit.id, onupdate='CASCADE', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    physical_quantity = Column(String(50))
    physical_unit = Column(String(50))
    aggregate_type = Column(String(50))
    value = Column(Float)
    start_datetime = Column(UTCDateTime, index=True)
    end_datetime = Column(UTCDateTime, index=True)

    peripheral = relationship(
        'Peripheral',
        back_populates='measurements',
    )
    kit = relationship(
        'Kit',
        back_populates='measurements',
    )


Peripheral.measurements = relationship(
    'Measurement',
    order_by=Measurement.end_datetime,
    back_populates='peripheral',
)
Kit.measurements = relationship(
    'Measurement',
    order_by=Measurement.end_datetime,
    back_populates='kit',
)


class DatabaseManager(object):
    """
    Provides thread-local scoped database session registry,
    as well as utility functions.
    """

    def __init__(self, host, port, username, password, database):
        self.engine = create_engine(
            (
                'postgresql+psycopg2://'
                f'{username}{":" + password if password else ""}'
                f'@{host}:{port}/{database}'
            ),
            isolation_level='READ COMMITTED',
        )

        # Create new connections in the case the engine is used from a forked
        # process.
        # See: https://docs.sqlalchemy.org/en/latest/core/pooling.html#using-connection-pools-with-multiprocessing
        @event.listens_for(self.engine, 'connect')
        def connect(dbapi_connection, connection_record):
            connection_record.info['pid'] = os.getpid()

        @event.listens_for(self.engine, 'checkout')
        def checkout(dbapi_connection, connection_record, connection_proxy):
            pid = os.getpid()
            if connection_record.info['pid'] != pid:
                connection_record.connection = connection_proxy.connection = None
                raise exc.DisconnectionError(
                    "Connection record belongs to pid %s, "
                    "attempting to check out in pid %s" %
                    (connection_record.info['pid'], pid)
                )

        session_factory = sessionmaker(bind=self.engine)

        # Thread-local session registry.
        self.Session = scoped_session(session_factory)

    def setup_schema(self):
        Base.metadata.create_all(self.engine)
        self.Session.commit()
        logger.info("New database prepared.")

    def insert_develop_data(self):
        import copy

        qt_temperature = QuantityType(
            physical_quantity = "Temperature",
            physical_unit = "Degrees Celsius",
            physical_unit_symbol = "°C",
        )
        self.Session.add(qt_temperature)

        qt_pressure = QuantityType(
            physical_quantity = "Pressure",
            physical_unit = "Hectopascal",
            physical_unit_symbol = "hPa",
        )
        self.Session.add(qt_pressure)

        qt_humidity = QuantityType(
            physical_quantity = "Humidity",
            physical_unit = "Percent",
            physical_unit_symbol = "%",
        )
        self.Session.add(qt_humidity)

        qt_concentration = QuantityType(
            physical_quantity = "Concentration",
            physical_unit = "Parts per million",
            physical_unit_symbol = "PPM",
        )
        self.Session.add(qt_concentration)

        qt_light_intensity = QuantityType(
            physical_quantity = "Light intensity",
            physical_unit = "Lux",
            physical_unit_symbol = "lx",
        )
        self.Session.add(qt_light_intensity)

        config_time_sleep = PeripheralConfigurationDefinition(
            name = "time_sleep",
            default_value = "3000",
            description = "Time to sleep between measurements in milliseconds.",
        )

        pd_v_temperature = PeripheralDefinition(
            name = "Virtual temperature sensor",
            description = (
                "A virtual temperature sensor using the environment simulation."
            ),
            brand="AstroPlant Virtual",
            model="Temperature",
            module_name = 'astroplant_simulation.sensors',
            class_name = 'Temperature',
            quantity_types=[
                qt_temperature,
            ],
            configuration_definitions=[
                copy.deepcopy(config_time_sleep)
            ],
        )
        self.Session.add(pd_v_temperature)

        pd_v_pressure = PeripheralDefinition(
            name = "Virtual pressure sensor",
            description = (
                "A virtual pressure sensor using the environment simulation."
            ),
            brand="AstroPlant Virtual",
            model="Pressure",
            module_name = "astroplant_simulation.sensors",
            class_name = "Pressure",
            quantity_types = [
                qt_pressure,
            ],
            configuration_definitions=[
                copy.deepcopy(config_time_sleep)
            ],
        )
        self.Session.add(pd_v_pressure)

        pd_v_barometer = PeripheralDefinition(
            name = "Virtual barometer",
            description = (
                "A virtual barometer using the environment simulation."
            ),
            brand="AstroPlant Virtual",
            model="Barometer",
            module_name = 'astroplant_simulation.sensors',
            class_name = 'Temperature',
            quantity_types=[
                qt_temperature,
                qt_pressure,
                qt_humidity,
            ],
            configuration_definitions=[
                copy.deepcopy(config_time_sleep)
            ],
        )
        self.Session.add(pd_v_barometer)

        pd_local_data_logger = PeripheralDefinition(
            name = "Local data logger",
            description = (
                "Logs aggregate measurement data locally."
            ),
            brand="AstroPlant",
            model="Logger",
            module_name='peripheral',
            class_name='LocalDataLogger',
            configuration_definitions=[
                PeripheralConfigurationDefinition(
                    name='storage_path',
                    default_value='./data',
                    description=(
                        "The storage path. Either absolute, or "
                        "relative to the program working directory."
                    ),
                )
            ],
        )
        self.Session.add(pd_local_data_logger)

        self.Session.commit()
