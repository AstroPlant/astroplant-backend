# -*- coding: utf-8 -*-
"""Aggregate message endpoints."""

from flask_restplus import Namespace, Resource
from flask_restplus import reqparse
from flask import make_response
import core.db_utils as db_utils

api = Namespace('Aggregate', description='Aggregate measage endpoints.')


query_parser = reqparse.RequestParser()
query_parser.add_argument('kit_serial', type=str, required=True, help="Kit serial.")
# The default value for the lower time boundary is the start of the UNIX Epoch.
query_parser.add_argument('time_from', type=str, required=False, help="Start time.", default="1970-01-01T00:00:00Z")
# The default value for the upper time boundary is the maximum UNIX time represented by a signed 32-bit number.
query_parser.add_argument('time_to', type=str, required=False, help="End time.", default="2038-01-19T03:14:08Z")


@api.route('/')
class RangeResource(Resource):

    @api.doc('Get aggregate measurements for a given kit.')
    @api.expect(query_parser, validate=True)
    def get(self):
        args = query_parser.parse_args()
        csv = db_utils.get_aggregate_csv(args['kit_serial'], args['time_from'], args['time_to'])

        response = make_response(csv)
        response.headers['Content-Disposition'] = 'attachment; filename=aggregate.csv'
        response.mimetype='text/csv'

        return response
