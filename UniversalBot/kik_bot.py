from kik.messages import messages_from_json, TextMessage, SuggestedResponseKeyboard, TextResponse, PictureMessage, \
	VideoMessage, StickerMessage, LinkMessage, UnknownMessage


from UniversalBot.AbstractHandler import Handler,AppInfo
from utilities import kik_service


class KikInfo(AppInfo):
	name = 'KIK'
	status = 'online'
	logo = 'img/bot/Kik_Messenger_Logo.png'
	link = 'https://bots.kik.com/#/geostrangerbot'


class KIK(Handler):

	def verify_signature(self, request):
		return self._service.verify_signature(request.headers.get('X-Kik-Signature'), request.get_data())

	def authorization(self):
		return

	def need_rewrite_commands(self):
		return False

	def expire_after_seconds(self, message):
		return

	def get_extra_data(self, message):
		pass

	_service = kik_service

	def get_attachments_url_from_message(self, message):

		if isinstance(message, StickerMessage):
			return [('image', message.sticker_url)]

		if isinstance(message, PictureMessage):
			return [('image', message.pic_url)]

		if isinstance(message, VideoMessage):
			return [('video', message.video_url)]
		return []

	def have_keyboard(self, message):
		return True

	def new_keyboard(self, *args):
		if not len(args):
			return False

		return SuggestedResponseKeyboard(responses=[TextResponse(x) for x in args])

	def bot_send_text(self, user_model, text, keyboard=None):
		message = TextMessage(
			to=user_model.conversation_id,
			body=text
		)
		if keyboard:
			message.keyboards.append(keyboard)

		self._service.send_messages([message])

	def bot_send_attachment(self, user_model, file_url, content_type, keyboard=None):

		if content_type and content_type.startswith('image'):
			message = PictureMessage(to=user_model.conversation_id, pic_url=file_url)
			if keyboard:
				message.keyboards.append(keyboard)

			self._service.send_messages([message])
			return

		if content_type and content_type.startswith('video'):
			message = VideoMessage(to=user_model.conversation_id, video_url=file_url)
			if keyboard:
				message.keyboards.append(keyboard)

			self._service.send_messages([message])
			return

		raise Exception('No compatility')

	def is_group(self, message):
		if message.chat_type == 'direct':
			return False
		return True

	def is_compatible(self, message):
		if isinstance(message, (LinkMessage, UnknownMessage)):
			return False
		return True

	def can_continue(self, message):
		return True

	def extract_message(self, request):
		return messages_from_json(request.json['messages'])

	def get_conversation_id_from_message(self, message):
		return message.from_user

	def get_user_language_from_message(self, message):
		return 'en'

	def get_text_from_message(self, message):
		if isinstance(message, TextMessage):
			return message.body
		return ''
