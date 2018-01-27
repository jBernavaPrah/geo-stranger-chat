import urlparse

import logging
import requests
import time


class SkypeSendException(Exception):
	pass


class SkypeBot(object):
	def __init__(self, client_id, key):
		self.skype_key = key
		self.client_id = client_id
		self._next_token = None
		self._token = None

	def _retrieve_token(self):
		try:
			payload = "grant_type=client_credentials&client_id=" + self.client_id + "&client_secret=" + self.skype_key + "&scope=https%3A%2F%2Fgraph.microsoft.com%2F.default"
			response = requests.post(
				"https://login.microsoftonline.com/common/oauth2/v2.0/token?client_id=" + self.client_id + "&client_secret=" + self.skype_key + "&grant_type=client_credentials&scope=https%3A%2F%2Fgraph.microsoft.com%2F.default",
				data=payload, headers={"Content-Type": "application/x-www-form-urlencoded"})
			data = response.json()
			self._token = data["access_token"]
			self._next_token = time.time() + 3300

		except Exception as e:
			logging.exception(e)
			time.sleep(0.7)
			self._retrieve_token()

	@property
	def token(self):
		if not self._token or not self._next_token or self._next_token < time.time():
			self._retrieve_token()

		return self._token

	def _send_request(self, service, conversation_id, payload):
		try:

			_url = urlparse.urljoin(service, '/v3/conversations/' + conversation_id + '/activities/')

			result = requests.post(_url,
			                       headers={"Authorization": "Bearer " + self.token,
			                                "Content-Type": "application/json"},
			                       json=payload)

			return result.status_code
		except Exception as e:
			raise SkypeSendException(e)

	def send_message(self, service, conversation_id, text, keyboard=None, reply_to_id=None):
		json_dict = {'type': 'message/text', 'text': text}

		if keyboard:
			json_dict['suggestedActions'] = keyboard.to_dict()

		if reply_to_id:
			json_dict['replyToId'] = reply_to_id

		self._send_request(service=service, conversation_id=conversation_id, payload=json_dict)

	def send_media(self, service, conversation_id, type_file, url, filename=''):

		payload = {
			"type": "message",
			"attachments": [{
				"contentType": type_file,
				"contentUrl": url,
				"filename": filename
			}]
		}

		self._send_request(service=service, conversation_id=conversation_id, payload=payload)
