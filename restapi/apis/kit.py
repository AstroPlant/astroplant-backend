# -*- coding: utf-8 -*-
"""Kit endpoints."""

from flask_restplus import Namespace, Resource
from flask_restplus import fields, marshal_with
import core.db_utils as db_utils

api = Namespace('Kit', description='Kit endpoints.')


@api.route('/')
class KitsResource(Resource):

    @api.doc('List kits.')
    def get(self):
        return db_utils.get_kits()


info_fields = {
    'serial': fields.String,
    'name': fields.String,
    'latitude': fields.String,
    'longitude': fields.String
}

info_model = api.model('Kit information', info_fields)

@api.route('/<kit_serial>')
@api.param('kit_serial', 'Kit serial.')
class KitResource(Resource):

    @api.doc('Get the kit information.')
    @api.marshal_with(info_model)
    def get(self, kit_serial):
        return db_utils.get_kit_info(kit_serial)


@api.route('/<kit_serial>/name')
@api.param('kit_serial', 'Kit serial.')
class KitNameResource(Resource):

    @api.doc('Get the kit name.')
    def get(self, kit_serial):
        return db_utils.get_kit_name(kit_serial)


location_fields = {
    'latitude': fields.String,
    'longitude': fields.String
}

location_model = api.model('Location', location_fields)

@api.route('/<kit_serial>/location')
@api.param('kit_serial', 'Kit serial.')
class KitLocationResource(Resource):

    @api.doc('Get the kit location.')
    @api.marshal_with(location_model)
    def get(self, kit_serial):
        return db_utils.get_kit_location(kit_serial)

    @api.doc('Specify the kit location.')
    @api.expect(location_model, validate=True)
    def post(self, kit_serial):
        latitude = api.payload['latitude']
        longitude = api.payload['longitude']
        db_utils.set_kit_location(kit_serial, latitude, longitude)
