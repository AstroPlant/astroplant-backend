import copy

from .specification import DatabaseManager, QuantityType, PeripheralDefinition


def insert_definitions(db: DatabaseManager, simulation_definitions):
    qt_temperature = QuantityType(
        physical_quantity="Temperature",
        physical_unit="Degrees Celsius",
        physical_unit_symbol="°C",
    )
    db.Session.add(qt_temperature)

    qt_pressure = QuantityType(
        physical_quantity="Pressure",
        physical_unit="Hectopascal",
        physical_unit_symbol="hPa",
    )
    db.Session.add(qt_pressure)

    qt_humidity = QuantityType(
        physical_quantity="Humidity", physical_unit="Percent", physical_unit_symbol="%",
    )
    db.Session.add(qt_humidity)

    qt_concentration = QuantityType(
        physical_quantity="Concentration",
        physical_unit="Parts per million",
        physical_unit_symbol="PPM",
    )
    db.Session.add(qt_concentration)

    qt_light_intensity = QuantityType(
        physical_quantity="Light intensity",
        physical_unit="Lux",
        physical_unit_symbol="lx",
    )
    db.Session.add(qt_light_intensity)

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
            symbol_location="astroplant_simulation.sensors",
            symbol="Temperature",
            quantity_types=[qt_temperature],
            configuration_schema={
                "type": "object",
                "title": "Configuration",
                "required": ["intervals"],
                "properties": {"intervals": config_measurement_interval},
            },
        )
        db.Session.add(pd_v_temperature)

        pd_v_pressure = PeripheralDefinition(
            name="Virtual pressure sensor",
            description=("A virtual pressure sensor using the environment simulation."),
            brand="AstroPlant Virtual",
            model="Pressure",
            symbol_location="astroplant_simulation.sensors",
            symbol="Pressure",
            quantity_types=[qt_pressure],
            configuration_schema={
                "type": "object",
                "title": "Configuration",
                "required": ["intervals"],
                "properties": {"intervals": config_measurement_interval},
            },
        )
        db.Session.add(pd_v_pressure)

        pd_v_barometer = PeripheralDefinition(
            name="Virtual barometer",
            description=("A virtual barometer using the environment simulation."),
            brand="AstroPlant Virtual",
            model="Barometer",
            symbol_location="astroplant_simulation.sensors",
            symbol="Barometer",
            quantity_types=[qt_temperature, qt_pressure, qt_humidity],
            configuration_schema={
                "type": "object",
                "title": "Configuration",
                "required": ["intervals"],
                "properties": {"intervals": config_measurement_interval},
            },
        )
        db.Session.add(pd_v_barometer)

        pd_v_heater = PeripheralDefinition(
            name="Virtual heater",
            description=("A virtual heater using the environment simulation."),
            brand="AstroPlant Virtual",
            model="Heater",
            symbol_location="astroplant_simulation.actuators",
            symbol="Heater",
            quantity_types=[],
            configuration_schema={"type": "null", "default": None},
            command_schema={
                "type": "number",
                "title": "Heater intensity",
                "minimum": 0,
                "maximum": 100,
            },
        )
        db.Session.add(pd_v_heater)

    pd_local_data_logger = PeripheralDefinition(
        name="Local data logger",
        description=("Logs aggregate measurement data locally."),
        brand="AstroPlant",
        model="Logger",
        symbol_location="peripheral",
        symbol="LocalDataLogger",
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
    db.Session.add(pd_local_data_logger)

    pd_am2302 = PeripheralDefinition(
        name="AstroPlant air temperature sensor",
        description="Measures air temperature and humidity.",
        brand="Asair",
        model="AM2302",
        quantity_types=[qt_temperature, qt_humidity],
        symbol_location="astroplant_peripheral_device_library.dht22",
        symbol="Dht22",
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
    db.Session.add(pd_am2302)

    pd_mh_z19 = PeripheralDefinition(
        name="AstroPlant air CO² sensor",
        description="Measures carbon dioxide concentration in the air.",
        brand=None,
        model="MH-Z19",
        quantity_types=[qt_concentration],
        symbol_location="astroplant_peripheral_device_library.mh_z19",
        symbol="MhZ19",
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
    db.Session.add(pd_mh_z19)

    pd_bh1750 = PeripheralDefinition(
        name="AstroPlant light sensor",
        description="Measures light intensity.",
        brand=None,
        model="BH1750",
        quantity_types=[qt_light_intensity],
        symbol_location="astroplant_peripheral_device_library.bh1750",
        symbol="Bh1750",
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
    db.Session.add(pd_bh1750)

    pd_ds18b20 = PeripheralDefinition(
        name="AstroPlant water temperature sensor",
        description="Measures water temperature.",
        brand=None,
        model="DS18B20",
        quantity_types=[qt_temperature],
        symbol_location="astroplant_peripheral_device_library.ds18b20",
        symbol="Ds18b20",
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
    db.Session.add(pd_ds18b20)

    pd_fans = PeripheralDefinition(
        name="AstroPlant fans",
        description="AstroPlant fans controlled through PWM.",
        brand=None,
        model="24V DC",
        symbol_location="astroplant_peripheral_device_library.pwm",
        symbol="Pwm",
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
    db.Session.add(pd_fans)

    pd_led_panel = PeripheralDefinition(
        name="AstroPlant LED panel",
        description="AstroPlant led panel controlled through PWM.",
        brand="AstroPlant",
        model="mk06",
        symbol_location="astroplant_peripheral_device_library.led_panel",
        symbol="LedPanel",
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
    db.Session.add(pd_led_panel)

    db.Session.commit()
