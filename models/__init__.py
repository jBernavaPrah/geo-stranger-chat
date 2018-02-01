import datetime

from mongoengine import *
from securemongoengine.fields import *
import config




connect(config.DATABASE, host=config.DATABASE_HOST, port=config.DATABASE_PORT)


class FileModel(Document):
	file_id = StringField()
	chat_type = StringField()
	file = FileField()
	created_at = DateTimeField(default=datetime.datetime.utcnow)


class MessageModel(Document):
	from_user = ReferenceField('UserModel')
	to_user = ReferenceField('UserModel')
	text = StringField()

	file = ListField(ReferenceField('FileModel'))
	created_at = DateTimeField(default=datetime.datetime.utcnow)


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
	updated_at = DateTimeField(default=datetime.datetime.utcnow)
	deleted_at = DateTimeField(default=None, unique_with=['chat_type', 'user_id'])

	@classmethod
	def pre_save(cls, sender, _document, **kwargs):
		if 'user_id' in sender:
			_document.user_id = user_id = encode(sender.user_id)

		_document.updated_at = datetime.datetime.utcnow()


if __name__ == '__main__':
	connect('dev')

	user = UserModel.objects.first()

	users = UserModel.objects(  # Q(id__ne=actual_user.id) & \
		Q(chat_with=None) & \
		Q(allow_search=True) & \
		Q(completed=True) & \
		Q(location__near=[45.5742348, 12.675057])) \
		.order_by("+updated_at").modify(chat_with=user, new=True)

	# for user in users:
	# print(user.id, user.location_text, user.updated_at)

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
	print(UserModel.objects.count())
