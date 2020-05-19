#!/usr/bin/env python

from astroplant_kafka_connector import __version__

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


setup(
    name="astroplant-kafka-connector",
    version=__version__,
    description="AstroPlant Kafka-to-database connector",
    author="Thomas Churchman",
    author_email="thomas@kepow.org",
    url="https://astroplant.io",
    packages=["astroplant_kafka_connector",],
    install_requires=[
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
    scripts=["scripts/astroplant-kafka-connector"],
)
