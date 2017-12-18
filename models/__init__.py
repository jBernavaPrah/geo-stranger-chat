import datetime
from mongoengine import *

connect('dev')


class Message(EmbeddedDocument):
	content = StringField()


class Conversation(Document):
	users = ListField(ReferenceField('User'))
	messages = ListField(EmbeddedDocumentField(Message))


class User(Document):
	name = StringField(required=True, max_length=200)
	chat_id = StringField(required=True)
	age = IntField()
	sex = IntField()
	actual_conversation = ListField(ReferenceField('Conversation'))

	created_at = DateTimeField(default=datetime.datetime.utcnow)

# tags = ListField(StringField(max_length=50))
# meta = {'allow_inheritance': True}


#user1 = User(name='Jure Bernava Prah', chat_id='telegram:123456789')
#user1.save()

user1 = ''

# post1 = TextPost(title='Using MongoEngine', content='See the tutorial')
# post1.tags = ['mongodb', 'mongoengine']
# post1.save()
#
# post2 = LinkPost(title='MongoEngine Docs', url='hmarr.com/mongoengine')
# post2.tags = ['mongoengine', 'documentation']
# post2.save()

# Iterate over all posts using the BlogPost superclass
print User.objects.count()
