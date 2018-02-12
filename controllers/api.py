from flask import Blueprint
from flask_restful import Api

from controllers.resources.ApiResources import UsersLocationAPI

api_template = Blueprint('api', __name__)
api = Api(api_template)

api.add_resource(UsersLocationAPI, '/users/location/', endpoint='users_location')
