from flask import Blueprint
from flask_restful import Api, Resource, reqparse

from models import UserModel

api_template = Blueprint('api', __name__)
api = Api(api_template)


class UsersLocationAPI(Resource):

	def __init__(self):
		self.reqparse = reqparse.RequestParser()
		self.reqparse.add_argument('south', type=float, required=True)
		self.reqparse.add_argument('west', type=float, required=True)
		self.reqparse.add_argument('north', type=float, required=True)
		self.reqparse.add_argument('east', type=float, required=True)

		super(UsersLocationAPI, self).__init__()

	def get(self):
		args = self.reqparse.parse_args()

		# loc.objects(point__geo_within_box=[ < bottom left coordinates >, < upper right coordinates >])
		users = UserModel.objects(location__geo_within_box=[(args.south, args.west), (args.north, args.east)])

		locations = []
		for user in users:
			locations.append(user.location)

		return locations



api.add_resource(UsersLocationAPI, '/users/location/', endpoint='users_location')
