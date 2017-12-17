import datetime
from mongoengine import *

connect('dev')


class User(Document):
	name = StringField(required=True, max_length=200)
	chat_id = StringField(required=True)
	age = IntField()
	sex = IntField()
	actual_conversation = ListField(ReferenceField(Conversation))

	created_at = DateTimeField(default=datetime.datetime.utcnow)

	tags = ListField(StringField(max_length=50))
	meta = {'allow_inheritance': True}


class Message(EmbeddedDocument):
	content = StringField()


class Conversation(Document):
	users = ListField(ReferenceField(User))
	messages = ListField(EmbeddedDocumentField(Message))


# post1 = TextPost(title='Using MongoEngine', content='See the tutorial')
# post1.tags = ['mongodb', 'mongoengine']
# post1.save()
#
# post2 = LinkPost(title='MongoEngine Docs', url='hmarr.com/mongoengine')
# post2.tags = ['mongoengine', 'documentation']
# post2.save()

# Iterate over all posts using the BlogPost superclass
for post in BlogPost.objects:
	print '===', post.title, '==='
	if isinstance(post, TextPost):
		print post.content
	elif isinstance(post, LinkPost):
		print 'Link:', post.url
	print

print BlogPost.objects.count()
