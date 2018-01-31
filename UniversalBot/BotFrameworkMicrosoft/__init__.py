
from urllib.parse import urljoin

import logging
import requests
import time


class SkypeSendException(Exception):
	pass


class Service(object):
	url = None
	from_user = None

	def __init__(self, client_id, key):

		self.Token = BotToken(client_id, key)

	def send_request(self, conversation_id, payload):

		if not 'from' in payload:
			payload['from'] = self.from_user

		# logging.debug(json.dumps(payload, indent=2))

		try:
			_url = urljoin(self.url, '/v3/conversations/' + conversation_id + '/activities/')
			result = requests.post(_url, headers={"Authorization": "Bearer " + self.Token.token,
												  "Content-Type": "application/json"},
								   json=payload)

			return result.status_code
		except Exception as e:
			raise SkypeSendException(e)


class WebChat(Service):
	url = 'https://webchat.botframework.com/'
	from_user = {'id': 'GeoStranger@hSqaACIqS9k'}


class Skype(Service):
	url = 'https://smba.trafficmanager.net/apis/'
	from_user = {'id': 'GeoStranger@hSqaACIqS9k'}


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

			# grant_type=client_credentials&client_id=MICROSOFT-APP-ID&client_secret=MICROSOFT-APP-PASSWORD&scope=

			# payload = "grant_type=&client_id=" + self.client_id + "&client_secret=" + self.skype_key + "&scope=https%3A%2F%2Fgraph.microsoft.com%2F.default"

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
	def __init__(self, service):
		self.Service = service

	def send_message(self, conversation_id, text, keyboard=None, reply_to_id=None):
		json_dict = {'type': 'message', 'text': text, 'textFormat': 'markdown'}

		if keyboard:
			json_dict['suggestedActions'] = keyboard.to_dict()

		if reply_to_id:
			json_dict['replyToId'] = reply_to_id

		self.Service.send_request(conversation_id=conversation_id, payload=json_dict)

	def send_media(self, conversation_id, type_file, url, filename=''):

		payload = {
			"type": "message",
			"attachmentLayout": 'list',
			"attachments": [{
				"contentType": type_file,
				"contentUrl": url,
				"filename": filename
			}]
		}

		self.Service.send_request(conversation_id=conversation_id, payload=payload)
