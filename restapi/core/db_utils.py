# -*- coding: utf-8 -*-
"""Database helper."""

def get_kits():
    return ['kit1', 'kit2']

def get_kit_info(kit_serial):
    return {'serial': 'kit1', 'name': 'USS Enterprise', 'latitude': 'here', 'longitude': 'there'}

def get_kit_name(kit_serial):
    return 'USS Enterprise'

def get_kit_location(kit_serial):
    return {'latitude': 'here', 'longitude': 'there'}

def set_kit_location(kit_serial):
    return

def get_aggregate_csv(serial, time_from, time_to):
    return """a,b
1,2
"""
