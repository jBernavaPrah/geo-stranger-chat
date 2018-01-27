import urlparse

import requests


class SkypeSendException(Exception):
	pass


class SkypeBot(object):
	def __init__(self, key):
		self.skype_key = key

	def _send_request(self, service, conversation_id, payload):
		try:

			_url = urlparse.urljoin(service, '/v3/conversations/' + conversation_id + '/activities/')

			result = requests.post(_url,
								   headers={"Authorization": "Bearer " + self.skype_key, "Content-Type": "application/json"},
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
