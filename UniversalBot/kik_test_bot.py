from kik import KikApi, Configuration
from kik.messages import messages_from_json, TextMessage, SuggestedResponseKeyboard, TextResponse

import config

from UniversalBot import Handler


class CustomHandler(Handler):
	Type = __name__

	_service = KikApi(config.KIK_TEST_BOT_USERNAME, config.KIK_TEST_BOT_API_KEY)

	def configuration(self):
		self._service.set_configuration(Configuration(webhook=config.KIK_TEST_BOT_WEBHOOK))

	def new_keyboard(self, *args):
		return SuggestedResponseKeyboard(responses=[TextResponse(x) for x in args])

	def remove_keyboard(self):
		return SuggestedResponseKeyboard()

	def real_send_text(self, user_id, text, keyboard=None):
		message = TextMessage(
			to=user_id,
			# chat_id=message.chat_id,
			body=text
		)

		message.keyboards.append(keyboard)

		self._service.send_messages([message])

	def real_send_photo(self, user_id, photo, caption=None, keyboard=None):
		pass

	def real_send_video(self, user_id, video_file, caption=None, keyboard=None, duration=None):
		pass

	def real_send_video_note(self, user_id, video_note_file, caption=None, duration=None, length=None, keyboard=None):
		pass

	def real_send_voice(self, user_id, voice_file, caption=None, duration=None, keyboard=None):
		pass

	def real_send_audio(self, user_id, audio, caption=None, keyboard=None, duration=None, performer=None, title=None):
		pass

	def real_send_document(self, user_id, document_file, caption=None, keyboard=None):
		pass

	def registry_commands(self):
		pass

	def process(self, json_data):
		pass

	def get_user_id_from_message(self, message):
		pass

	def get_user_language_from_message(self, message):
		pass

	def has_file_message(self, message):
		pass

	def get_text_from_message(self, message):
		pass

	def get_caption_from_message(self, message):
		pass

	def get_data(self, message):
		pass

	def get_file(self, file_id):
		pass
