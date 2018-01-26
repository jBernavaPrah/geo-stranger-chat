# -*- coding: utf-8 -*-
from UniversalBot import Handler
from UniversalBot.SkypeBot import types


class CustomHandler(Handler):
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
		pass

	def real_send_photo(self, user_model, file_model, caption=None, keyboard=None):
		pass

	def real_send_video(self, user_model, file_model, caption=None, keyboard=None, duration=None):
		pass

	def real_send_audio(self, user_model, file_model, caption=None, keyboard=None, duration=None, performer=None,
						title=None):
		pass

	def real_send_document(self, user_model, file_model, caption=None, keyboard=None):
		pass

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
