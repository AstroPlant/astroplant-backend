#!/usr/bin/env python

from astroplant_database import __version__
from setuptools import setup

setup(
    name="astroplant-database",
    version=__version__,
    description="AstroPlant database",
    author="Thomas Churchman",
    author_email="thomas@kepow.org",
    url="https://astroplant.io",
    packages=[
        "astroplant_database",
        "astroplant_database.alembic",
        "astroplant_database.alembic.versions",
    ],
    include_package_data=True,
    install_requires=[
        "sqlalchemy~=1.4",
    ],
    extras_require={
        "cli": [
            "click~=8.0",
            "psycopg2~=2.8",
            "alembic~=1.3",
        ]
    },
    scripts=["scripts/astroplant-database"],
)
