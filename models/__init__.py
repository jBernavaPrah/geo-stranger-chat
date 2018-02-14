import datetime

from mongoengine import *

import config

connect(config.DATABASE, host=config.DATABASE_HOST, port=config.DATABASE_PORT)


# meta = {
# 	'indexes': [
# 		{'fields': ['created_at'], 'expireAfterSeconds': 3600}
# 	]
# }

class ProxyUrlModel(Document):
	url = StringField(required=True)
	created_at = DateTimeField(default=datetime.datetime.utcnow)
	meta = {
		'indexes': [
			{'fields': ['created_at'], 'expireAfterSeconds': 60 * 5}
		]
	}


class BotModel(EmbeddedDocument):
	chat_type = StringField()
	extra_data = DictField()
	user_id = StringField()


class ConversationModel(Document):
	# bots = EmbeddedDocumentField('BotModel')

	extra_data = DictField()
	chat_type = StringField(required=True)
	conversation_id = StringField(required=True)

	language = StringField()

	location = PointField(default=None)
	location_text = StringField(default=None)

	completed = BooleanField(default=False)

	last_engage_at = DateTimeField()
	chat_with = ReferenceField('ConversationModel', default=None)
	first_time_chat = BooleanField(default=True)

	is_searchable = BooleanField(default=False)

	next_function = StringField(default=None)

	messages_sent = IntField(default=0)
	messages_received = IntField(default=0)

	expire_at = DateTimeField()

	created_at = DateTimeField(default=datetime.datetime.utcnow)

	deleted_at = DateTimeField(default=None, unique_with=['chat_type', 'conversation_id'])


# meta = {
# 	'indexes': [
# 		{'fields': ['expire_at'], 'expireAfterSeconds': 60 * 5}
# 	]
# }


# meta = {'strict': False}


if __name__ == '__main__':
	connect('dev')

	# user = UserModel.objects.first()

	users = ConversationModel.objects(
		Q(chat_with=None) & \
		# Q(allow_search=True) & \
		Q(completed=True)) \
		.order_by("+created_at") \
		.order_by("+messages_sent") \
		.order_by("+messages_received")

	for user in users:
		print(user.id, user.location_text, user.created_at, user.messages_received, user.messages_sent)

	# user3 = User(name='Pippo', chat_type='telegram', chat_id='3', location=[45.672641, 11.934923])
	# user3.save()
	#
	# user2 = User(name='Pinco Pallino', chat_type='telegram', chat_id='2', location=[45.6772697, 11.9186683])
	# user2.save()
	#
	# user1 = User(name='Jure Bernava Prah', chat_type='telegram', chat_id='1', location=[45.6753059, 11.9187222])
	# user1.save()

	# user_telegram_123456789 = User.objects(chat_type='telegram', chat_id='123456789').first()

	# user_telegram_123456789.location = [45.6753059,11.9187222]
	# user_telegram_123456789.save()

	# users = User.objects(chat_type='telegram', chat_id='123456789').first()
	#
	# for user in UserModel.objects(Q(count_actual_conversation=0) | Q(count_actual_conversation=None)):
	# 	print user.name, user.location, user.count_actual_conversation
	#
	# print "===="
	#
	# user1 = UserModel.objects(chat_id='1', chat_type='telegram').first()
	#
	# for user in UserModel.objects(
	# 		Q(id__ne=user1.id) & \
	# 		Q(count_actual_conversation=0) & \
	# 		Q(location__near=user1.location)):
	# 	print user.name, user.location, user.count_actual_conversation
	#
	# print "===="

	# print User.objects(
	# 	Q(id__ne=user1.id) & \
	# 	Q(count_actual_conversation=0) & \
	# 	Q(location__near=user1.location)).update_one(inc__count_actual_conversation=1)

	print("====")

	# post1 = TextPost(title='Using MongoEngine', content='See the tutorial')
	# post1.tags = ['mongodb', 'mongoengine']
	# post1.save()
	#
	# post2 = LinkPost(title='MongoEngine Docs', url='hmarr.com/mongoengine')
	# post2.tags = ['mongoengine', 'documentation']
	# post2.save()

	# Iterate over all posts using the BlogPost superclass
	print(ConversationModel.objects.count())
