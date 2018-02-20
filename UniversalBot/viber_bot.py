from kik.messages import TextMessage, PictureMessage, VideoMessage, StickerMessage
from viberbot.api.messages import FileMessage
from viberbot.api.viber_requests import ViberMessageRequest, ViberSubscribedRequest, ViberFailedRequest

from UniversalBot.AbstractHandler import Handler
from utilities import viber_service


class ViberBot(Handler):
	_service = viber_service

	def verify_signature(self, request):
		if not self._service.verify_signature(request.get_data(), request.headers.get('X-Viber-Content-Signature')):
			return False
		return True

	def authorization(self):
		pass

	def expire_after_seconds(self, message):
		pass

	def get_conversation_id_from_message(self, message):
		return message.sender.id

	def get_user_language_from_message(self, message):

		if 'user' in message and 'language' in message.user:
			return message.user.language

		user_data = self._service.get_user_details(message.sender.id)
		print('Remember to save it correctyl!')
		print(user_data)

		return 'en'

	def get_attachments_url_from_message(self, message):

		pass

	def get_text_from_message(self, message):
		pass

	def new_keyboard(self, *args):
		if not len(args):
			return {
				"Type": "keyboard",
				"Buttons": []

			}

		actions = []
		for a in args:
			actions.append({"ActionType": "reply",
							"ActionBody": a, 'text': a})

		return {
			"Type": "keyboard",
			"Buttons": [actions]
		}

	def have_keyboard(self, message):
		return True

	def bot_send_text(self, user_model, text, keyboard=None):
		self._service.send_messages(user_model.conversation_id, [
			TextMessage(text=text, keyboards=keyboard)
		])

	def bot_send_attachment(self, user_model, file_url, file_type, keyboard=None):

		if file_type and file_type.startswith('image'):
			return self._service.send_messages(user_model.conversation_id, [
				PictureMessage(media=file_url)
			])

		if file_type and file_type.startswith('video'):
			return self._service.send_messages(user_model.conversation_id, [
				VideoMessage(media=file_url)
			])

		if file_type and file_type.startswith('audio'):
			raise Exception

		return self._service.send_messages(user_model.conversation_id, [
			FileMessage(media=file_url)
		])

	def is_group(self, message):
		return False

	def can_continue(self, message):
		if isinstance(message, (ViberMessageRequest, ViberSubscribedRequest, ViberFailedRequest)):
			return True
		return False

	def is_compatible(self, message):
		if isinstance(message, (TextMessage, PictureMessage, VideoMessage, StickerMessage)):
			return True
		return False

	def extract_message(self, request):
		return self._service.parse_request(request.get_data())

	def get_extra_data(self, message):
		return False

	def need_rewrite_commands(self):
		return False
