from telebot import types, apihelper

import config
from UniversalBot.AbstractHandler import Handler
from utilities import telegram_service


class Telegram(Handler):
	_service = telegram_service

	def authorization(self):
		return

	def need_rewrite_commands(self):
		return False

	def expire_after_seconds(self, message):
		return

	def get_extra_data(self, message):
		pass

	def is_compatible(self, message):
		return True

	def can_continue(self, message):
		return True

	def extract_message(self, request):
		return types.Update.de_json(request.get_data().decode('utf-8')).message

	def is_group(self, message):
		if message.chat.type == 'private':
			return False
		return True

	def have_keyboard(self, message):
		return True

	def new_keyboard(self, *args):

		if not len(args):
			return types.ReplyKeyboardRemove(selective=False)

		markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

		button = []
		if len(args) == 2:
			for text in args:
				button.append(types.KeyboardButton(text))

			return markup.row(*button)

		for text in args:
			markup.row(types.KeyboardButton(text))

		return markup

	def bot_send_text(self, user_model, text, keyboard=None):

		self._service.send_message(user_model.conversation_id, text, disable_web_page_preview=True,
								   parse_mode='markdown',
								   reply_markup=keyboard, reply_to_message_id=None)

	def bot_send_attachment(self, user_model, file_url, content_type, keyboard=None):

		if content_type and content_type.startswith('image'):
			return self._service.send_photo(user_model.conversation_id, photo=file_url, reply_markup=keyboard)

		if content_type and content_type.startswith('video'):
			return self._service.send_video(user_model.conversation_id, file_url, reply_markup=keyboard)

		if content_type and content_type.startswith('audio'):
			return self._service.send_audio(user_model.conversation_id, file_url, reply_markup=keyboard, )

		return self._service.send_document(user_model.conversation_id, file_url, reply_markup=keyboard)

	def get_conversation_id_from_message(self, message):
		return message.chat.id

	def get_user_language_from_message(self, message):
		return message.from_user.language_code

	def get_text_from_message(self, message):
		if hasattr(message, 'text') and message.text:
			return message.text.strip()

		if hasattr(message, 'caption') and message.caption:
			return message.caption.strip()

		return ''

	def get_attachments_url_from_message(self, message):

		_f = None

		if hasattr(message, 'sticker') and message.sticker:
			_f = message.sticker

		if hasattr(message, 'photo') and message.photo:
			if isinstance(message.photo, (tuple, list)):
				_f = message.photo[-1]
			else:
				_f = message.photo

		if hasattr(message, 'video') and message.video:
			_f = message.video

		if hasattr(message, 'video_note') and message.video_note:
			_f = message.video_note

		if hasattr(message, 'document') and message.document:
			_f = message.document

		if hasattr(message, 'audio') and message.audio:
			_f = message.audio

		if hasattr(message, 'voice') and message.voice:
			_f = message.voice

		if _f:
			file_info = self._service.get_file(_f.file_id)
			file_url = apihelper.FILE_URL.format(config.TELEGRAM_BOT_KEY, file_info.file_path)
			return [file_url]

		return []
