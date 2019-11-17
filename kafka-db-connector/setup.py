#!/usr/bin/env python

import kafka_db_connector
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(name='kafka_db_connector',
      version=kafka_db_connector.__version__,
      description='AstroPlant Kafka->database connector',
      author='Thomas Churchman',
      author_email='thomas@kepow.org',
      url='https://astroplant.io',
      packages=['kafka_db_connector',],
      install_requires=requirements,
     )
