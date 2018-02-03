from flask import Blueprint
from flask_restful import Api, Resource, reqparse

api_template = Blueprint('api', __name__)
api = Api(api_template)


class UsersLocationAPI(Resource):

	def __init__(self):
		self.reqparse = reqparse.RequestParser()
		self.reqparse.add_argument('latitude', type=str, required=True)
		self.reqparse.add_argument('longitude', type=str, required=True)
		self.reqparse.add_argument('range', type=int, required=True)

		super(UsersLocationAPI, self).__init__()

	def get(self):
		args = self.reqparse.parse_args()

		# return all users!

		return []


api.add_resource(UsersLocationAPI, '/users/location/', endpoint='users_location')
