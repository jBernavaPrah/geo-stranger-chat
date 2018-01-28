# -*- coding: utf-8 -*-
import config
from UniversalBot import Handler
from UniversalBot.SkypeBot import types, SkypeBot


class CustomHandler(Handler):
	def get_additional_data_from_message(self, message):
		return dict(serviceUrl=message['serviceUrl'])

	Type = __name__
	_service = SkypeBot(config.SKYPE_TEST_BOT_ID, config.SKYPE_TEST_BOT_KEY)

	def configuration(self):
		pass
		# self._service.generate_token()

	def new_keyboard(self, *args):
		actions = []
		for a in args:
			actions.append(types.KeyboardAction(a, a))

		return types.Keyboard(*actions)

	def remove_keyboard(self):
		return types.Keyboard()

	def real_send_text(self, user_model, text, keyboard=None):
		self._service.send_message(user_model.additional_data['serviceUrl'], user_model.user_id, text, keyboard=keyboard)

	def real_send_photo(self, user_model, file_model, caption=None, keyboard=None):
		file_url = self._url_download_document(file_model)

		self._service.send_media(user_model.additional_data['serviceUrl'], user_model.user_id, file_model.file.content_type, file_url, file_model.file.filename)

	def real_send_video(self, user_model, file_model, caption=None, keyboard=None, duration=None):
		file_url = self._url_download_document(file_model)

		self._service.send_media(user_model.additional_data['serviceUrl'], user_model.user_id, file_model.file.content_type, file_url, file_model.file.filename)

	def real_send_audio(self, user_model, file_model, caption=None, keyboard=None, duration=None, performer=None,
						title=None):
		file_url = self._url_download_document(file_model)

		self._service.send_media(user_model.additional_data['serviceUrl'], user_model.user_id, file_model.file.content_type, file_url, file_model.file.filename)

	def real_send_document(self, user_model, file_model, caption=None, keyboard=None):
		file_url = self._url_download_document(file_model)

		self._service.send_media(user_model.additional_data['serviceUrl'], user_model.user_id, file_model.file.content_type, file_url, file_model.file.filename)

	def registry_commands(self):
		pass

	def process(self, request):
		message = request.json

		self.generic_command(message)

	# for message in messages:

	def get_user_id_from_message(self, message):
		return message['from']['id']

	def get_user_language_from_message(self, message):
		return 'en'

	def get_images_url_from_message(self, message):
		images_url = []
		if 'attachments' in message and len(message['attachments']):
			for attachment in message['attachments']:
				if attachment['contentType'].startWith('image'):
					images_url.append(attachment['contentUrl'])

		return images_url

	def get_videos_url_from_message(self, message):
		images_url = []
		if 'attachments' in message and len(message['attachments']):
			for attachment in message['attachments']:
				if attachment['contentType'].startWith('video'):
					images_url.append(attachment['contentUrl'])

		return images_url

	def get_documents_url_from_message(self, message):
		images_url = []
		if 'attachments' in message and len(message['attachments']):
			for attachment in message['attachments']:
				if attachment['contentType'].startWith('audio') and attachment['contentType'].startWith('video') and attachment['contentType'].startWith('image'):
					images_url.append(attachment['contentUrl'])

		return images_url

	def get_audios_url_from_message(self, message):
		images_url = []
		if 'attachments' in message and len(message['attachments']):
			for attachment in message['attachments']:
				if attachment['contentType'].startWith('audio'):
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
