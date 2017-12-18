import datetime
from mongoengine import *
from mongoengine.queryset.visitor import Q

connect('dev')

class Message(EmbeddedDocument):
	content = StringField()


class Conversation(Document):
	users = ListField(ReferenceField('User'))
	messages = ListField(EmbeddedDocumentField(Message))
	created_at = DateTimeField(default=datetime.datetime.utcnow)


class User(Document):
	chat_type = StringField(required=True)
	chat_id = StringField(required=True, unique_with='chat_type')
	name = StringField()
	age = IntField()
	sex = IntField()
	location = PointField()
	count_actual_conversation = IntField(default=0)
	actual_conversation = ListField(ReferenceField('Conversation'))
	created_at = DateTimeField(default=datetime.datetime.utcnow)


# tags = ListField(StringField(max_length=50))
# meta = {'allow_inheritance': True}




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

	for user in User.objects(Q(count_actual_conversation=0) | Q(count_actual_conversation=None)):
		print user.name, user.location, user.count_actual_conversation

	print "===="

	user1 = User.objects(chat_id='1', chat_type='telegram').first()

	for user in User.objects(
							Q(id__ne=user1.id) & \
							Q(count_actual_conversation=0) & \
					Q(location__near=user1.location)):
		print user.name, user.location, user.count_actual_conversation

	print "===="

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
	print User.objects.count()
