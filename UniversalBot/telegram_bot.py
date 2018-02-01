import telebot
from flask import Response
from telebot import types, apihelper

import config
from UniversalBot import Handler


class CustomHandler(Handler):
	def get_additional_data_from_message(self, message):
		pass

	Type = __name__

	_service = telebot.TeleBot(config.TELEGRAM_BOT_KEY, threaded=False)

	def configuration(self):
		self._service.set_webhook(url='https://%s%s' % (config.SERVER_NAME, config.TELEGRAM_BOT_WEBHOOK))

	def new_keyboard(self, *args):
		markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

		button = []
		if len(args) == 2:
			for text in args:
				button.append(types.KeyboardButton(text))

			return markup.row(*button)

		for text in args:
			markup.row(types.KeyboardButton(text))

		return markup

	def remove_keyboard(self):
		return types.ReplyKeyboardRemove(selective=False)

	def real_send_text(self, user_model, text, keyboard=None):

		self._service.send_message(user_model.user_id, text, disable_web_page_preview=True, parse_mode='markdown',
								   reply_markup=keyboard, reply_to_message_id=None)

	def real_send_photo(self, user_model, file_url, keyboard=None):



		self._service.send_photo(user_model.user_id, photo=file_url.file, reply_markup=keyboard)

	def real_send_video(self, user_model, file_url, keyboard=None):

		self._service.send_video(user_model.user_id, file_url.file, reply_markup=keyboard)

	def real_send_audio(self, user_model, file_url, keyboard=None):

		self._service.send_audio(user_model.user_id, file_url.file, reply_markup=keyboard, )

	def real_send_document(self, user_model, file_url, keyboard=None):
		self._service.send_document(user_model.user_id, file_url.file, reply_markup=keyboard)

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

	def get_images_url_from_message(self, message):

		if hasattr(message, 'sticker') and message.sticker:
			_f = message.sticker

			file_info = self._service.get_file(_f.file_id)
			file_url = apihelper.FILE_URL.format(config.TELEGRAM_BOT_KEY, file_info.file_path)

			return [file_url]

		if hasattr(message, 'photo') and message.photo:
			if isinstance(message.photo, (tuple, list)):
				_f = message.photo[-1]
			else:
				_f = message.photo

			file_info = self._service.get_file(_f.file_id)
			file_url = apihelper.FILE_URL.format(config.TELEGRAM_BOT_KEY, file_info.file_path)

			return [file_url]

	def get_videos_url_from_message(self, message):
		if hasattr(message, 'video') and message.video:
			_f = message.video
			file_info = self._service.get_file(_f.file_id)
			file_url = apihelper.FILE_URL.format(config.TELEGRAM_BOT_KEY, file_info.file_path)
			return [file_url]

		if hasattr(message, 'video_note') and message.video_note:
			_f = message.video_note
			file_info = self._service.get_file(_f.file_id)
			file_url = apihelper.FILE_URL.format(config.TELEGRAM_BOT_KEY, file_info.file_path)
			return [file_url]

	def get_documents_url_from_message(self, message):
		if hasattr(message, 'document') and message.document:
			_f = message.document
			file_info = self._service.get_file(_f.file_id)
			file_url = apihelper.FILE_URL.format(config.TELEGRAM_BOT_KEY, file_info.file_path)
			return [file_url]

	def get_audios_url_from_message(self, message):
		if hasattr(message, 'audio') and message.audio:
			_f = message.audio
			file_info = self._service.get_file(_f.file_id)
			file_url = apihelper.FILE_URL.format(config.TELEGRAM_BOT_KEY, file_info.file_path)
			return [file_url]

		if hasattr(message, 'voice') and message.voice:
			_f = message.voice
			file_info = self._service.get_file(_f.file_id)
			file_url = apihelper.FILE_URL.format(config.TELEGRAM_BOT_KEY, file_info.file_path)
			return [file_url]

	# COMMANDS

	def registry_commands(self):

		# self._service.add_message_handler({
		# 	'function': self.welcome_command,
		# 	'filters': dict(commands=['start'])
		# })
		#
		# self._service.add_message_handler({
		# 	'function': self.location_command,
		# 	'filters': dict(commands=['location'])
		# })
		#
		# self._service.add_message_handler({
		# 	'function': self.help_command,
		# 	'filters': dict(commands=['help'])
		# })
		#
		# self._service.add_message_handler({
		# 	'function': self.stop_command,
		# 	'filters': dict(commands=['stop'])
		# })
		#
		# self._service.add_message_handler({
		# 	'function': self.search_command,
		# 	'filters': dict(commands=['search'])
		# })
		#
		# self._service.add_message_handler({
		# 	'function': self.delete_command,
		# 	'filters': dict(commands=['delete'])
		# })
		#
		# self._service.add_message_handler({
		# 	'function': self.terms_command,
		# 	'filters': dict(commands=['terms'])
		# })

		self._service.add_message_handler({
			'function': self.generic_command,
			'filters': dict(func=lambda message: True,
							content_types=['text', 'audio', 'document', 'photo', 'sticker', 'video', 'video_note',
										   'voice'])
		})

		self._service.add_message_handler({
			'function': self.not_compatible,
			'filters': dict(func=lambda message: True)
		})

	def process(self, request):
		json_string = request.get_data().decode('utf-8')
		update = telebot.types.Update.de_json(json_string)
		self._service.process_new_updates([update])
		return Response(status=200)
