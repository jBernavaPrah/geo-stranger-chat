import os
from urllib.parse import urljoin

import logging
import requests
import time


class WebChatToken(object):
	def __init__(self, key):
		self.key = key

	def token(self):
		response = requests.get("https://webchat.botframework.com/api/tokens",
								headers={'Authorization': 'BotConnector %s' % self.key}
								)
		return response.json()


class BotToken(object):
	_token = None
	_next_token = None
	_on_retrieve = False

	def __init__(self, client_id, key):
		self.client_id = client_id
		self.key = key

	def generate_token(self, force=False):
		if force:
			self._retrieve_token()
		return self.token

	@property
	def token(self):
		if not self._token or not self._next_token or self._next_token < time.time():
			self._retrieve_token()

		return self._token

	def _retrieve_token(self):
		try:

			payload = {'grant_type': 'client_credentials', 'client_id': self.client_id, 'client_secret': self.key,
					   'scope': 'https://api.botframework.com/.default'}

			response = requests.post("https://login.microsoftonline.com/botframework.com/oauth2/v2.0/token",
									 data=payload)

			data = response.json()
			self._token = data["access_token"]
			self._next_token = time.time() + 3300

		except Exception as e:
			logging.exception(e)
			time.sleep(0.7)
			self._retrieve_token()


class BotFrameworkMicrosoft(object):
	def __init__(self, client_id, key):
		self.Token = BotToken(client_id, key)

	def _send_request(self, url, conversation_id, payload):
		_url = urljoin(url, '/v3/conversations/' + conversation_id + '/activities/')
		result = requests.post(_url, headers={"Authorization": "Bearer " + self.Token.token,
											  "Content-Type": "application/json"},
							   json=payload)

		result.raise_for_status()

	def send_message(self, url, from_user, conversation_id, text, keyboard=None, reply_to_id=None):
		json_dict = {'type': 'message', 'text': text, 'textFormat': 'markdown'}

		json_dict['from'] = from_user

		if keyboard:
			json_dict['suggestedActions'] = keyboard.to_dict()

		if reply_to_id:
			json_dict['replyToId'] = reply_to_id

		self._send_request(url, conversation_id=conversation_id, payload=json_dict)

	def send_media(self, url, from_user, conversation_id, content_url, content_type, keyboard=None):

		payload = {
			"type": "message",
			"attachmentLayout": 'list',
			"attachments": [{
				"contentType": content_type,
				"contentUrl": content_url,
				"filename": os.path.basename(url)
			}],
			'from': from_user
		}

		if keyboard:
			payload['suggestedActions'] = keyboard.to_dict()

		self._send_request(url, conversation_id=conversation_id, payload=payload)
