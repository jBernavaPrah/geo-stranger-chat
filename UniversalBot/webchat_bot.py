# -*- coding: utf-8 -*-
import config
from UniversalBot import Handler
from UniversalBot.BotFrameworkMicrosoft import types, BotFrameworkMicrosoft, WebChat as _WebChat

webchat_service = BotFrameworkMicrosoft(_WebChat(config.MICROSOFT_BOT_ID, config.MICROSOFT_BOT_KEY))


class WebChat(Handler):
	_service = webchat_service

	def new_keyboard(self, *args):
		actions = []
		for a in args:
			actions.append(types.KeyboardAction(a, a))

		return types.Keyboard(*actions)

	def remove_keyboard(self):
		return types.Keyboard()

	def bot_send_text(self, user_model, text, keyboard=None):
		self._service.send_message(user_model.conversation_id, text,
								   keyboard=keyboard)

	def bot_send_attachment(self, user_model, file_url, content_type, keyboard=None):
		self._service.send_media(user_model.conversation_id, file_url, content_type)

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

		if 'channelId' in message and message['channelId'] != self.__class__.__name__.lower():
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
			return message['locale']
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



