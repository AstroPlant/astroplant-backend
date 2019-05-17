from flask import Blueprint
from flask_restplus import Api

from .kit import api as ns_kit
from .aggregate import api as ns_aggregate


blueprint = Blueprint('AstroPlant Backend REST API', __name__)
api = Api(blueprint)

api.add_namespace(ns_kit, path='/kit')
api.add_namespace(ns_aggregate, path='/aggregate')
