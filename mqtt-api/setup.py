#!/usr/bin/env python

import mqtt_api

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="mqtt_api",
    version=mqtt_api.__version__,
    description="AstroPlant MQTT API",
    author="Thomas Churchman",
    author_email="thomas@kepow.org",
    url="https://astroplant.io",
    packages=["mqtt_api",],
    install_requires=requirements,
)
