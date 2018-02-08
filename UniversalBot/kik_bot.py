from flask import Response
from flask_babel import gettext
from kik import KikApi, Configuration

from kik.messages import messages_from_json, TextMessage, SuggestedResponseKeyboard, TextResponse, PictureMessage, \
	VideoMessage, StickerMessage, ScanDataMessage, LinkMessage, UnknownMessage

import config
from UniversalBot import Handler

kik_service = KikApi(config.KIK_BOT_USERNAME, config.KIK_BOT_KEY)
kik_service.set_configuration(
	Configuration(webhook='https://%s%s' % (config.SERVER_NAME, config.KIK_BOT_WEBHOOK)))


class KIK(Handler):
	def get_extra_data(self, message):
		pass

	_service = kik_service

	def get_attachments_url_from_message(self, message):

		if isinstance(message, StickerMessage):
			return [message.sticker_url]

		if isinstance(message, PictureMessage):
			return [message.pic_url]

		if isinstance(message, VideoMessage):
			return [message.video_url]
		return []

	def new_keyboard(self, *args):
		return SuggestedResponseKeyboard(responses=[TextResponse(x) for x in args])

	def remove_keyboard(self):
		return None

	def bot_send_text(self, user_model, text, keyboard=None):
		message = TextMessage(
			to=user_model.conversation_id,
			# chat_id=message.chat_id,
			body=text
		)
		if keyboard:
			message.keyboards.append(keyboard)

		self._service.send_messages([message])

	def bot_send_attachment(self, user_model, file_url, content_type, keyboard=None):

		text = self.translate('download_file', file_url=file_url)

		message = TextMessage(
			to=user_model.conversation_id,
			# chat_id=message.chat_id,
			body=text
		)

		if content_type and content_type.startswith('image'):
			message = PictureMessage(to=user_model.conversation_id, pic_url=file_url)

		if content_type and content_type.startswith('video'):
			message = VideoMessage(to=user_model.conversation_id, video_url=file_url)

		if content_type and content_type.startswith('audio'):
			file_url = self._url_play_audio(file_url)

			text = self.translate('play_audio', file_url=file_url)

			message = TextMessage(
				to=user_model.conversation_id,
				# chat_id=message.chat_id,
				body=text
			)

		if keyboard:
			message.keyboards.append(keyboard)

		self._service.send_messages([message])

	def is_group(self, message):
		if message.chatType == 'direct':
			return False
		return True

	def can_continue(self, message):
		if isinstance(message, (ScanDataMessage, LinkMessage, UnknownMessage)):
			return False
		return True

	def extract_message(self, request):
		return messages_from_json(request.json['messages'])

	def get_conversation_id_from_message(self, message):
		return message.chatId

	def get_user_language_from_message(self, message):
		return 'en'

	def get_text_from_message(self, message):
		if hasattr(message, 'body'):
			return message.body
		return ''
