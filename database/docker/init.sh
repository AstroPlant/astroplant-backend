#!/usr/bin/env bash

export DATABASE_URL=postgresql+psycopg2://astroplant@/astroplant

astroplant-database create-schema
astroplant-database insert-definitions --simulation-definitions
