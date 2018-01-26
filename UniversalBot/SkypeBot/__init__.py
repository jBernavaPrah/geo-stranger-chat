import requests


class SkypeSendException(Exception):
	pass


class SkypeBot(object):
	def __init__(self, key):
		self.skype_key = key

	def _send_request(self, service, conversation_id, payload):
		try:
			r = requests.post(service + '/v3/conversations/' + conversation_id + '/activities/',
							  headers={"Authorization": "Bearer " + self.skype_key, "Content-Type": "application/json"},
							  json=payload)

			r.raise_for_status()
		except Exception as e:
			raise SkypeSendException(e)

	def send_message(self, service, conversation_id, text, keyboard=None):
		payload = {
			"type": "message",
			"text": text
		}
		self._send_request(service=service, conversation_id=conversation_id, payload=payload)

	def send_media(self, service, conversation_id, type_file, url):

		payload = {
			"type": "message",
			"attachments": [{
				"contentType": type_file,
				"contentUrl": url
			}]
		}

		self._send_request(service=service, conversation_id=conversation_id, payload=payload)
