import telebot
from telebot import types

import config
from UniversalBot import Handler


class TelegramHandler(Handler):
	Type = __name__
	_service = telebot.TeleBot(config.GEOSTRANGER_TEST_KEY, threaded=False)

	def __init__(self):
		self._service.set_webhook(url='https://%s%s' % (config.SERVER_NAME, config.WEBHOOK_GEOSTRANGER_TEST))

	def _get_user_id(self, message):
		return message.from_user.id

	def _get_user_language(self, message):
		return message.from_user.language_code

	def _get_text(self, message):
		if hasattr(message, 'text'):
			return message.text.encode('utf8').strip()
		return None

	def _get_data(self, message):
		if hasattr(message, 'data'):
			return message.data.encode('utf8').strip()
		return None

	def _yes_no_keyboard(self, yes_text, no_text):
		markup = types.ReplyKeyboardMarkup()
		itembtna = types.KeyboardButton(yes_text)
		itembtnv = types.KeyboardButton(no_text)
		return markup.row(itembtna, itembtnv)

	def _remove_keyboard(self):
		return types.ReplyKeyboardRemove(selective=False)

	@_service.message_handler(commands=['start'])
	def welcome_command(self, message):
		self._on_welcome_message(message)

	@_service.message_handler(commands=['location'])
	def location_command(self, message):
		self._on_location_change(message)

	@_service.message_handler(commands=['help'])
	def help_command(self, message):

		pass

	@_service.message_handler(func=lambda message: True,
	                          content_types=['text', 'audio', 'document', 'photo', 'sticker', 'video', 'video_note',
	                                         'voice', 'location', 'contact'])
	def command_handler(self, message):
		self._handle_message(message)

	def send_text(self, user_id, text, keyboard=None):
		self._service.send_message(user_id, text, disable_web_page_preview=True, parse_mode='markdown',
		                           reply_markup=keyboard, reply_to_message_id=None)

	def send_photo(self, user_id, photo, caption=None):
		self._service.send_photo(user_id, photo=photo, caption=None, reply_markup=None, reply_to_message_id=None)

	def send_video(self, user_id, video_id_or_file, caption=None):
		self._service.send_video(user_id, video_id_or_file, duration=None, caption=None, reply_to_message_id=None,
		                         reply_markup=None, disable_notification=None, timeout=None)

	def send_audio(self, user_id, audio_id_or_file, caption=None, duration=None):
		self._service.send_audio(user_id, audio, caption=caption, duration=duration,performer=None,title=None)

	def process(self, json_data):
		# json_string = request.get_data().decode('utf-8')
		update = telebot.types.Update.de_json(json_data)
		self._service.process_new_updates([update])

	def handlers(self):
		pass
