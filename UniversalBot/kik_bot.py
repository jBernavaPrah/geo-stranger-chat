import mimetypes

from flask import Response
from kik import KikApi, Configuration

from kik.messages import messages_from_json, TextMessage, SuggestedResponseKeyboard, TextResponse, PictureMessage, \
	VideoMessage, StickerMessage, ScanDataMessage, LinkMessage, UnknownMessage

import config

from UniversalBot import Handler, trans_message


class CustomHandler(Handler):
	def get_attachments_url_from_message(self, message):

		if isinstance(message, StickerMessage):
			return [message.sticker_url]

		if isinstance(message, PictureMessage):
			return [message.pic_url]

		if isinstance(message, VideoMessage):
			return [message.video_url]
		return []

	def get_additional_data_from_message(self, message):
		pass

	Type = __name__

	_service = KikApi(config.KIK_BOT_USERNAME, config.KIK_BOT_KEY)

	def configuration(self):
		self._service.set_configuration(
			Configuration(webhook='https://%s%s' % (config.SERVER_NAME, config.KIK_BOT_WEBHOOK)))

	def new_keyboard(self, *args):
		return SuggestedResponseKeyboard(responses=[TextResponse(x) for x in args])

	def remove_keyboard(self):
		return None

	def real_send_text(self, user_model, text, keyboard=None):
		message = TextMessage(
			to=user_model.user_id,
			# chat_id=message.chat_id,
			body=text
		)
		if keyboard:
			message.keyboards.append(keyboard)

		self._service.send_messages([message])

	def real_send_attachment(self, user_model, file_url, content_type, keyboard=None):

		text = trans_message(user_model.language, 'download_file').format(url=file_url)

		message = TextMessage(
			to=user_model.user_id,
			# chat_id=message.chat_id,
			body=text
		)

		if content_type and content_type.startswith('image'):
			message = PictureMessage(to=user_model.user_id, pic_url=file_url)

		if content_type and content_type.startswith('video'):
			message = VideoMessage(to=user_model.user_id, video_url=file_url)

		if content_type and content_type.startswith('audio'):
			file_url = self._url_play_audio(file_url)

			text = trans_message(user_model.language, 'play_audio').format(url=file_url)

			message = TextMessage(
				to=user_model.user_id,
				# chat_id=message.chat_id,
				body=text
			)

		if keyboard:
			message.keyboards.append(keyboard)

		self._service.send_messages([message])

	def registry_commands(self):
		pass

	def process(self, request):

		if not self._service.verify_signature(request.headers.get('X-Kik-Signature'), request.get_data()):
			return Response(status=403)

		messages = messages_from_json(request.json['messages'])

		for message in messages:

			if isinstance(message, (ScanDataMessage, LinkMessage, UnknownMessage)):
				return self.not_compatible(message)

			self.generic_command(message)

		return Response(status=200)

	def get_user_id_from_message(self, message):
		return message.from_user

	def get_user_language_from_message(self, message):
		return 'en'

	def get_text_from_message(self, message):
		if hasattr(message, 'body'):
			return message.body
		return ''

	def get_caption_from_message(self, message):
		return ''

	def get_data(self, message):
		if hasattr(message, 'metadata'):
			return message.metadata
		return ''
