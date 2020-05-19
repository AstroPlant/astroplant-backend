#!/usr/bin/env python

from astroplant_mqtt_connector import __version__

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


setup(
    name="astroplant-mqtt-connector",
    version=__version__,
    description="AstroPlant MQTT Connector",
    author="Thomas Churchman",
    author_email="thomas@kepow.org",
    url="https://astroplant.io",
    packages=["astroplant_mqtt_connector",],
    install_requires=[
        "paho-mqtt~=1.4",
        "kafka-python~=1.4",
        "pycapnp~=0.6",
        "sqlalchemy~=1.3",
        "psycopg2~=2.8",
        "click~=7.0",
        "astroplant-database==" + __version__,
    ],
    include_package_data=True,
    # Required for capnp, see https://github.com/capnproto/pycapnp/issues/72
    zip_safe=False,
    scripts=["scripts/astroplant-mqtt-connector"],
)
