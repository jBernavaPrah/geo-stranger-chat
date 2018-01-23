import telebot
from telebot import types

import config
from UniversalBot import Handler


class CustomHandler(Handler):
	Type = __name__

	_service = telebot.TeleBot(config.GEOSTRANGER_TEST_KEY, threaded=False)

	def configuration(self):
		self._service.set_webhook(url='https://%s%s' % (config.SERVER_NAME, config.TELEGRAM_TEST_BOT_WEBHOOK))

	def new_keyboard(self, *args):
		markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
		button = []
		for text in args:
			button.append(types.KeyboardButton(text))

		return markup.row(*button)

	def remove_keyboard(self):
		return types.ReplyKeyboardRemove(selective=False)

	def real_send_text(self, user_id, text, keyboard=None):
		self._service.send_message(user_id, text, disable_web_page_preview=True, parse_mode='markdown',
								   reply_markup=keyboard, reply_to_message_id=None)

	def real_send_photo(self, user_id, photo, caption=None, keyboard=None):
		self._service.send_photo(user_id, photo=photo, caption=caption, reply_markup=keyboard, reply_to_message_id=None,
								 disable_notification=None)

	def real_send_video(self, user_id, video_file, caption=None, keyboard=None, duration=None):
		self._service.send_video(user_id, video_file, duration=duration, caption=caption, reply_to_message_id=None,
								 reply_markup=keyboard, disable_notification=None, timeout=None)

	def real_send_voice(self, user_id, voice_file, caption=None, duration=None, keyboard=None):
		self._service.send_voice(user_id, voice_file, caption=caption, duration=duration, reply_to_message_id=None,
								 reply_markup=keyboard, disable_notification=None, timeout=None)

	def real_send_audio(self, user_id, audio_file, caption=None, keyboard=None, duration=None, performer=None,
						title=None):
		self._service.send_audio(user_id, audio_file, caption=caption, duration=duration, performer=performer,
								 title=title, reply_to_message_id=None, reply_markup=keyboard, )

	def real_send_video_note(self, user_id, video_note_file, caption=None, duration=None, length=None, keyboard=None):

		self._service.send_video_note(user_id, video_note_file, duration=duration, length=length,
									  reply_to_message_id=None,
									  reply_markup=keyboard, disable_notification=None, timeout=None)

	def real_send_document(self, user_id, document_file, caption=None, keyboard=None):
		self._service.send_document(user_id, document_file, reply_to_message_id=None, caption=caption,
									reply_markup=keyboard,
									disable_notification=None, timeout=None)

	def get_user_id_from_message(self, message):
		return message.from_user.id

	def get_user_language_from_message(self, message):
		return message.from_user.language_code

	def get_text_from_message(self, message):
		if hasattr(message, 'text') and message.text:
			return message.text.encode('utf8').strip()
		return ''

	def get_data(self, message):
		if hasattr(message, 'data') and message.data:
			return message.data.encode('utf8').strip()
		return ''

	def get_caption_from_message(self, message):
		if hasattr(message, 'caption') and message.caption:
			return message.caption.encode('utf8').strip()
		return ''

	def get_file(self, file_id):
		file_info = self._service.get_file(file_id)
		return self._service.download_file(file_info.file_path)

	def has_file_message(self, message):

		if hasattr(message, 'photo') and message.photo:
			if isinstance(message.photo, (tuple, list)):
				_f = message.photo[-1]
			else:
				_f = message.photo
			return _f.file_id, 'photo'

		if hasattr(message, 'video') and message.video:
			_f = message.video
			return _f.file_id, 'video'

		if hasattr(message, 'video_note') and message.video_note:
			_f = message.video_note
			return _f.file_id, 'video_note'

		if hasattr(message, 'audio') and message.audio:
			_f = message.audio
			return _f.file_id, 'audio'

		if hasattr(message, 'voice') and message.voice:
			_f = message.voice
			return _f.file_id, 'voice'

		if hasattr(message, 'document') and message.document:
			_f = message.document
			return _f.file_id, 'document'

		return None, None

	# COMMANDS

	def registry_commands(self):

		self._service.add_message_handler({
			'function': self.welcome_command,
			'filters': dict(commands=['start'])
		})

		self._service.add_message_handler({
			'function': self.location_command,
			'filters': dict(commands=['location'])
		})

		self._service.add_message_handler({
			'function': self.help_command,
			'filters': dict(commands=['help'])
		})

		self._service.add_message_handler({
			'function': self.not_compatible,
			'filters': dict(func=lambda message: True, content_types=['sticker', 'location', 'contact'])
		})

		self._service.add_message_handler({
			'function': self.stop_command,
			'filters': dict(commands=['stop'])
		})

		self._service.add_message_handler({
			'function': self.search_command,
			'filters': dict(commands=['search'])
		})

		self._service.add_message_handler({
			'function': self.delete_command,
			'filters': dict(commands=['delete'])
		})

		self._service.add_message_handler({
			'function': self.terms_command,
			'filters': dict(commands=['terms'])
		})

		self._service.add_message_handler({
			'function': self.generic_command,
			'filters': dict(func=lambda message: True,
							content_types=['text', 'audio', 'document', 'photo', 'sticker', 'video', 'video_note',
										   'voice'])
		})

	def process(self, request):
		json_string = request.get_data().decode('utf-8')
		update = telebot.types.Update.de_json(json_string)
		self._service.process_new_updates([update])
