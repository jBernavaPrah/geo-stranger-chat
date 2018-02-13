# -*- coding: utf-8 -*-
import config
from UniversalBot.AbstractHandler import Handler
from UniversalBot.BotFrameworkMicrosoft import types
from utilities import microsoft_service


class MicrosoftBot(Handler):
	_service = microsoft_service

	def need_rewrite_commands(self, message):
		if message['channelId'] == 'skype':
			return True
		return False

	def need_expire(self, message):
		if message['channelId'] == 'webchat':
			return True
		return False

	def new_keyboard(self, *args):
		actions = []
		for a in args:
			actions.append(types.KeyboardAction(a, a))

		return types.Keyboard(*actions)

	def remove_keyboard(self):
		return types.Keyboard()

	def bot_send_text(self, user_model, text, keyboard=None):
		self._service.send_message(user_model.extra_data['serviceUrl'], user_model.extra_data['from'],
								   user_model.conversation_id, text, keyboard=keyboard)

	def bot_send_attachment(self, user_model, file_url, content_type, keyboard=None):
		self._service.send_media(user_model.extra_data['serviceUrl'], user_model.extra_data['from'],
								 user_model.conversation_id, file_url, content_type, keyboard=keyboard)

	def get_extra_data(self, message):
		return {'serviceUrl': message['serviceUrl'], 'from': message['recipient']}

	def is_compatible(self, message):
		return True

	def can_continue(self, message):

		if 'type' in message and message['type'] == 'deleteUserData':
			return False

		if 'type' in message and message['type'] == 'ping':
			return False

		if message['type'] == 'conversationUpdate' and 'membersAdded' in message:

			if message['membersAdded'][0]['id'].startswith(config.MICROSOFT_BOT_NAME):

				return True
			else:
				return False

		return True

	def is_group(self, message):
		if message['type'] == 'conversationUpdate' and 'membersAdded' in message:

			if len(message['membersAdded']) > 2:
				return True
		return False

	def extract_message(self, request):
		return request.json

	def get_conversation_id_from_message(self, message):
		return message['conversation']['id']

	def get_user_language_from_message(self, message):

		if 'locale' in message:
			return message['locale'][:2]

		if 'entities' in message:
			x = message['entities'][0]
			if 'locale' in x:
				return x['locale'][:2]
		return 'en'

	def get_attachments_url_from_message(self, message):
		images_url = []
		if 'attachments' in message and len(message['attachments']):
			for attachment in message['attachments']:
				images_url.append(attachment['contentUrl'])

		return images_url

	def get_text_from_message(self, message):
		if 'text' in message:
			return message['text']
		return ''
