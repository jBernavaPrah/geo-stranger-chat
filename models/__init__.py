import datetime
import json

from mongoengine import *
import config

connect(config.DATABASE, host=config.DATABASE_HOST, port=config.DATABASE_PORT)


class MessageModel(Document):
	user = ReferenceField('UserModel')
	text = StringField()
	document = FileField()
	photo = FileField()
	audio = FileField()
	video = FileField()
	video_note = FileField()
	voice = FileField()
	raw = StringField()
	created_at = DateTimeField(default=datetime.datetime.utcnow)

	def from_chat(self, message):
		if message.text:
			self.text = message.text

		if message.document:
			self.document = message.document

		if message.photo:
			self.photo = message.photo

		if message.video:
			self.video = message.video

		if message.video_note:
			self.video_note = message.video_note

		if message.voice:
			self.voice = message.voice


# meta = {
# 	'indexes': [
# 		{'fields': ['created_at'], 'expireAfterSeconds': 3600}
# 	]
# }



class UserModel(Document):
	chat_type = StringField(required=True)
	user_id = StringField(required=True)

	name = StringField()
	age = IntField()
	sex = StringField()
	language = StringField()

	location = PointField(default=None)
	location_text = StringField(default=None)

	completed = BooleanField(default=False)

	chat_with = ReferenceField('UserModel', default=None)
	first_time_chat = BooleanField(default=True)

	allow_search = BooleanField(default=False)

	next_function = StringField(default=None)

	created_at = DateTimeField(default=datetime.datetime.utcnow)
	deleted_at = DateTimeField(default=None, unique_with=['chat_type', 'user_id'])


# tags = ListField(StringField(max_length=50))
# meta = {'allow_inheritance': True}

class LoggingModel(Document):
	raw = DictField()
	created_at = DateTimeField(default=datetime.datetime.utcnow)


if __name__ == '__main__':
	connect('dev')

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

	print "===="

	# post1 = TextPost(title='Using MongoEngine', content='See the tutorial')
	# post1.tags = ['mongodb', 'mongoengine']
	# post1.save()
	#
	# post2 = LinkPost(title='MongoEngine Docs', url='hmarr.com/mongoengine')
	# post2.tags = ['mongoengine', 'documentation']
	# post2.save()

	# Iterate over all posts using the BlogPost superclass
	print UserModel.objects.count()
