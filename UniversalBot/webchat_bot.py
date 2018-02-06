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
		self._service.send_message(user_model.user_id, text,
								   keyboard=keyboard)

	def bot_send_attachment(self, user_model, file_url, content_type, keyboard=None):
		self._service.send_media(user_model.user_id, file_url, content_type)

	def process(self, request):
		message = request.json
		self.generic_command(message)

	# for message in messages:

	def get_user_id_from_message(self, message):
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

	def get_caption_from_message(self, message):
		return ''

	def get_data(self, message):
		return ''
