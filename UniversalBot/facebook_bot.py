# -*- coding: utf-8 -*-
from fbmq import QuickReply, Attachment, Event

from UniversalBot.AbstractHandler import Handler
from utilities import facebook_service


class FacebookBot(Handler):
	_service = facebook_service

	def authorization(self):
		return

	def need_rewrite_commands(self):
		return False

	def expire_after_seconds(self, message):
		return

	def have_keyboard(self, message):
		return True

	def new_keyboard(self, *args):

		if not len(args):
			return []

		actions = []
		for a in args:
			actions.append(QuickReply(title=a, payload=a))

		return actions

	def bot_send_text(self, user_model, text, keyboard=None):

		self._service.send(user_model.conversation_id, text, quick_replies=keyboard)

	def bot_send_attachment(self, user_model, file_url, content_type, keyboard=None):

		if content_type and content_type.startswith('image'):
			return self._service.send(user_model.conversation_id, Attachment.Image(file_url), quick_replies=keyboard)

		if content_type and content_type.startswith('video'):
			return self._service.send(user_model.conversation_id, Attachment.Video(file_url), quick_replies=keyboard)

		if content_type and content_type.startswith('audio'):
			return self._service.send(user_model.conversation_id, Attachment.Audio(file_url), quick_replies=keyboard)

		return self._service.send(user_model.conversation_id, Attachment.File(file_url), quick_replies=keyboard)

	def get_extra_data(self, message):
		return

	def is_compatible(self, message):
		return True

	def can_continue(self, message):

		return True

	def is_group(self, message):
		return False

	def extract_message(self, request):
		data = request.json

		for entry in data.get("entry"):
			messagings = entry.get("messaging",[])
			for messaging in messagings:
				event = Event(messaging)
				yield event

	def get_conversation_id_from_message(self, message):
		return message.sender_id

	def get_user_language_from_message(self, message):

		user_profile = self._service.get_user_profile(message.sender_id)

		return user_profile.get('locale', 'en')

	def get_attachments_url_from_message(self, message):
		images_url = []
		for attachment in message.message_attachments:
			if attachment.get('type', '') in ['audio', 'file', 'image', 'video']:
				images_url.append(attachment.get('payload', []).get('url'))

		return images_url

	def get_text_from_message(self, message):
		return message.message_text
