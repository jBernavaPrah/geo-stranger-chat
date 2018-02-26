# -*- coding: utf-8 -*-
import config
from UniversalBot.AbstractHandler import Handler, AppInfo
from UniversalBot.BotFrameworkMicrosoft import types
from utilities import microsoft_service


class SkypeInfo(AppInfo):
	name = 'Skype'
	status = 'online'
	logo = 'img/bot/SKYPE_logo_box.png'
	link = 'https://join.skype.com/bot/%s' % config.MICROSOFT_BOT_ID
	info = 'Be sure to use last Version of Skype. See FAQ.'


class MicrosoftBot(Handler):
	_service = microsoft_service

	def verify_signature(self, request):
		# TODO study this signature...
		return True

	def authorization(self):
		return {'Authorization': 'Bearer %s' % self._service.Token.token}

	def need_rewrite_commands(self):
		if 'channelId' in self.current_conversation.extra_data and self.current_conversation.extra_data[
			'channelId'] == 'skype':
			return True
		return

	def expire_after_seconds(self, message):
		if message['channelId'] == 'webchat':
			return 600
		return False

	def have_keyboard(self, message):
		if 'channelId' in message and message['channelId'] == 'skype':
			return False
		return True

	def new_keyboard(self, *args):

		if not len(args):
			return types.Keyboard()

		actions = []
		for a in args:
			actions.append(types.KeyboardAction(a, a))

		return types.Keyboard(*actions)

	def bot_send_text(self, user_model, text, keyboard=None):
		self._service.send_message(user_model.extra_data['serviceUrl'], user_model.extra_data['from'],
								   user_model.conversation_id, text, keyboard=keyboard)

	def bot_send_attachment(self, user_model, file_url, file_type, keyboard=None):
		self._service.send_media(user_model.extra_data['serviceUrl'], user_model.extra_data['from'],
								 user_model.conversation_id, file_url, file_type, keyboard=keyboard)

	def get_extra_data(self, message):
		return {'serviceUrl': message['serviceUrl'], 'from': message['recipient'], 'channelId': message['channelId']}

	def is_compatible(self, message):
		# TODO: Check if there are some other type that are not comaptible with geostrager!
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
		if message['type'] == 'conversationUpdate' and len(message.get('membersAdded', [])) > 2:
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

		for attachment in message.get('attachments', []):
			# ho anche attachment['name'], dove viene indiacto il nome del file....

			images_url.append((attachment['contentType'], attachment['contentUrl']))

		return images_url

	def get_text_from_message(self, message):
		return message.get('text', '')
