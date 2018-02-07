from flask import Blueprint
from flask_restful import Api, Resource, reqparse

from models import ConversationModel

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
		pipeline = [
			{'$group':
				 {'_id': {'location': '$location'},
				  'count': {'$sum': 1}
				  }
			 }]

		# print((args.south, args.west), (args.north, args.east))

		# loc.objects(point__geo_within_box=[ < bottom left coordinates >, < upper right coordinates >])
		users = ConversationModel.objects(location__geo_within_box=[(args.west, args.south), (args.east, args.north)]) \
			.aggregate(*pipeline)

		locations = []
		for user in users:
			# locations.append(user.location)
			locations.append({'location': user.get('_id', {}).get('location'), 'count': user.get('count')})

		return locations


api.add_resource(UsersLocationAPI, '/users/location/', endpoint='users_location')
