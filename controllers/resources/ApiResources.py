import datetime

from flask_restful import Resource, reqparse
from mongoengine import Q

from models import ConversationModel


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
				 {'_id': {'location': '$location', 'location_text': '$location_text'}}
			 }]

		# print((args.south, args.west), (args.north, args.east))

		# loc.objects(point__geo_within_box=[ < bottom left coordinates >, < upper right coordinates >])
		users = ConversationModel.objects(deleted_at=None, completed=True,
										  location__geo_within_box=[(args.west, args.south), (args.east, args.north)]) \
			.aggregate(*pipeline)

		locations = []
		for user in users:
			# locations.append(user.location)
			locations.append(
				{'location': user.get('_id', {}).get('location'),
				 'location_text': user.get('_id', {}).get('location_text')})

		return locations


class ConversationsNextApi(Resource):
	def __init__(self):
		self.reqparse = reqparse.RequestParser()
		self.reqparse.add_argument('_id', type=str, required=True)
		self.reqparse.add_argument('limit', type=int, default=1)

		super(ConversationsNextApi, self).__init__()

	def get(self):
		args = self.reqparse.parse_args()

		conversation = ConversationModel.objects(id=args._id).first()

		if not conversation:
			return []

		return ConversationModel.objects(Q(id__nin=[conversation.id]) & \
										 Q(chat_with=None) & \
										 (Q(is_searchable=True) | Q(allow_search=True)) & \
										 Q(completed=True) & \
										 Q(location__near=conversation.location) & \
										 (Q(expire_at__exists=False) | Q(
											 expire_at__gte=datetime.datetime.utcnow()))) \
			.order_by("+created_at") \
			.order_by("+messages_sent") \
			.order_by("+messages_received") \
			.order_by("+last_engage_at").limit(args.limit).to_json()
