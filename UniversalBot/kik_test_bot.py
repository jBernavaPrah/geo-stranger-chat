import requests
from flask import Response
from kik import KikApi, Configuration

from kik.messages import messages_from_json, TextMessage, SuggestedResponseKeyboard, TextResponse, PictureMessage, \
	VideoMessage, StartChattingMessage
from kik.messages.responses import SuggestedResponse

import config

from UniversalBot import Handler, trans_message


class MyTextResponse(SuggestedResponse):
	"""
	   A text response, as documented at `<https://dev.kik.com/#/docs/messaging#suggested-response-keyboard>`_.
	   """

	def __init__(self, body, metadata=None):
		super(MyTextResponse, self).__init__(type='text', metadata=metadata)
		self.body = body
		self.metadata = metadata

	@classmethod
	def property_mapping(cls):
		mapping = super(MyTextResponse, cls).property_mapping()
		mapping.update({'body': 'body', 'metadata': 'metadata'})
		return mapping


class CustomHandler(Handler):
	Type = __name__

	_service = KikApi(config.KIK_TEST_BOT_USERNAME, config.KIK_TEST_BOT_API_KEY)

	def configuration(self):
		self._service.set_configuration(
			Configuration(webhook='https://%s%s' % (config.SERVER_NAME, config.KIK_TEST_BOT_WEBHOOK)))

	def new_keyboard(self, *args):
		return SuggestedResponseKeyboard(responses=[MyTextResponse(x, x) for x in args])

	def remove_keyboard(self):
		return SuggestedResponseKeyboard()

	def real_send_text(self, user_model, text, keyboard=None):
		message = TextMessage(
			to=user_model.user_id,
			# chat_id=message.chat_id,
			body=text
		)
		if keyboard:
			message.keyboards.append(keyboard)

		self._service.send_messages([message])

	def real_send_photo(self, user_model, file_model, caption=None, keyboard=None):

		file_url = self._url_download_file(file_model)

		message = PictureMessage(to=user_model.user_id, pic_url=file_url)
		if keyboard:
			message.keyboards.append(keyboard)

		self._service.send_messages([message])

	def real_send_video(self, user_model, file_model, caption=None, keyboard=None, duration=None):
		file_url = self._url_download_file(file_model)

		message = VideoMessage(to=user_model.user_id, video_url=file_url)

		if keyboard:
			message.keyboards.append(keyboard)

		self._service.send_messages([message])

	def real_send_video_note(self, user_model, file_model, caption=None, duration=None, length=None, keyboard=None):
		file_url = self._url_download_file(file_model)

		message = VideoMessage(to=user_model.user_id, video_url=file_url)

		if keyboard:
			message.keyboards.append(keyboard)

		self._service.send_messages([message])

	def real_send_voice(self, user_model, file_model, caption=None, duration=None, keyboard=None):

		file_url = self._url_play_audio(file_model)

		text = trans_message(user_model.language, 'play_voice')
		text.format(url=file_url)

		message = TextMessage(
			to=user_model.user_id,
			# chat_id=message.chat_id,
			body=text
		)
		if keyboard:
			message.keyboards.append(keyboard)

		self._service.send_messages([message])

	def real_send_audio(self, user_model, file_model, caption=None, keyboard=None, duration=None, performer=None,
						title=None):
		file_url = self._url_play_audio(file_model)

		text = trans_message(user_model.language, 'play_audio')
		text.format(url=file_url)

		message = TextMessage(
			to=user_model.user_id,
			# chat_id=message.chat_id,
			body=text
		)
		if keyboard:
			message.keyboards.append(keyboard)

		self._service.send_messages([message])

	def real_send_document(self, user_model, file_model, caption=None, keyboard=None):
		file_url = self._url_download_file(file_model)

		text = trans_message(user_model.language, 'download_file')
		text.format(url=file_url)

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
			self.generic_command(message)

		return Response(status=200)

	def get_user_id_from_message(self, message):
		return message.from_user

	def get_user_language_from_message(self, message):
		return 'en'

	def get_file_id_and_type_from_message(self, message):
		if isinstance(message, PictureMessage):
			return message.pic_url, 'photo'

		if isinstance(message, VideoMessage):
			return message.video_url, 'video'

		return None, None

	def get_text_from_message(self, message):
		if hasattr(message, 'body'):
			return message.body

	def get_caption_from_message(self, message):
		return ''

	def get_data(self, message):
		if hasattr(message, 'metadata'):
			return message.metadata

	def get_file(self, file_id):
		return requests.get(file_id)
