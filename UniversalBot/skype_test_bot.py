# -*- coding: utf-8 -*-
import config
from UniversalBot import Handler
from UniversalBot.SkypeBot import types, SkypeBot


class CustomHandler(Handler):
	_service = SkypeBot(config.SKYPE_TEST_BOT_KEY)

	def configuration(self):
		pass

	def new_keyboard(self, *args):
		actions = []
		for a in args:
			actions.append(types.KeyboardAction(a, a))

		return types.Keyboard(*actions)

	def remove_keyboard(self):
		return types.Keyboard()

	def real_send_text(self, user_model, text, keyboard=None):
		self._service.send_message(user_model.service_url, user_model.user_id, text, keyboard=keyboard)

	def real_send_photo(self, user_model, file_model, caption=None, keyboard=None):
		file_url = self._url_download_document(file_model)

		self._service.send_media(user_model.service_url, user_model.user_id, file_model.file.content_type, file_url, file_model.file.filename)

	def real_send_video(self, user_model, file_model, caption=None, keyboard=None, duration=None):
		file_url = self._url_download_document(file_model)

		self._service.send_media(user_model.service_url, user_model.user_id, file_model.file.content_type, file_url, file_model.file.filename)

	def real_send_audio(self, user_model, file_model, caption=None, keyboard=None, duration=None, performer=None,
						title=None):
		file_url = self._url_download_document(file_model)

		self._service.send_media(user_model.service_url, user_model.user_id, file_model.file.content_type, file_url, file_model.file.filename)

	def real_send_document(self, user_model, file_model, caption=None, keyboard=None):
		file_url = self._url_download_document(file_model)

		self._service.send_media(user_model.service_url, user_model.user_id, file_model.file.content_type, file_url, file_model.file.filename)

	def registry_commands(self):
		pass

	def process(self, request):
		pass

	def get_user_id_from_message(self, message):
		pass

	def get_user_language_from_message(self, message):
		pass

	def get_image_url_from_message(self, message):
		pass

	def get_video_url_from_message(self, message):
		pass

	def get_document_url_from_message(self, message):
		pass

	def get_audio_url_from_message(self, message):
		pass

	def get_text_from_message(self, message):
		pass

	def get_caption_from_message(self, message):
		pass

	def get_data(self, message):
		pass
