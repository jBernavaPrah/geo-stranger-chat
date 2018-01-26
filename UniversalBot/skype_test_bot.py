# -*- coding: utf-8 -*-
import requests


class SkypeSendException(Exception):
	pass


class SkypeBot(object):
	def __init__(self, key):
		self.skype_key = key

	# text should be UTF-8 and has a 320 character limit

	def _send_request(self, service, conversation_id, payload):
		try:
			r = requests.post(service + '/v3/conversations/' + conversation_id + '/activities/',
							  headers={"Authorization": "Bearer " + self.skype_key, "Content-Type": "application/json"},
							  json=payload)

			r.raise_for_status()
		except Exception as e:
			raise SkypeSendException(e)

	def send_message(self, service, conversation_id, text):
		payload = {
			"type": "message",
			"text": text
		}
		self._send_request(service=service, conversation_id=conversation_id, payload=payload)

	def send_media(self, service, conversation_id, type, url):

		payload = {
			"type": "message",
			"attachments": [{
				"contentType": type,
				"contentUrl": url
			}]
		}

		self._send_request(service=service, conversation_id=conversation_id, payload=payload)


# openUrl  URL to be opened in the built-in browser.
# imBack  Text of message which client will sent back to bot as ordinary chat message. All other participants will see that was posted to the bot and who posted this.
# postBack  Text of message which client will post to bot. Client applications will not display this message.
# call  Destination for a call in following format: "tel:123123123123"
# playAudio  playback audio container referenced by URL
# playVideo  playback video container referenced by URL
# showImage  show image referenced by URL
# downloadFile  download file referenced by URL
# signin  OAuth flow URL


def create_buttons(type, title, value):
	buttons_dict = {}
	buttons_dict["type"] = type
	buttons_dict["title"] = title
	# buttons_dict['image'] = image
	buttons_dict["value"] = value

	return buttons_dict


def create_card_image(url, alt):
	img_dict = {}
	img_dict["url"] = url
	img_dict["alt"] = alt
	return img_dict


def create_card_attachment(type, title, subtitle, text, images, buttons):
	card_attachment = {}
	card_attachment = {
		"contentType": "application/vnd.microsoft.card." + type,
		"content": {
			"title": title,
			"subtitle": subtitle,
			"text": text,
			"images": images,
			"buttons": buttons
		}
	}

	return card_attachment


def send_card(token, service, sender, type, card_attachment, summary, text):
	try:
		payload = {
			"type": "message",
			"attachmentLayout": type,
			"summary": summary,
			"text": text,
			"attachments": card_attachment
		}

		r = requests.post(service + '/v3/conversations/' + sender + '/activities/',
						  headers={"Authorization": "Bearer " + token, "Content-Type": "application/json"},
						  json=payload)
		print payload
		print r
	except Exception as e:
		print e
		pass


# typing action not yet supported

def send_action(token, service, sender):
	try:
		payload = {
			"type": "typing"
		}
		r = requests.post(service + '/v3/conversations/' + sender + '/activities/',
						  headers={"Authorization": "Bearer " + token, "Content-Type": "application/json"},
						  json=payload)
		print payload
		print r
	except Exception as e:
		print e
		pass


def create_animation(type, url, images, title, subtitle, text, buttons):
	card_animation = {}
	card_animation = {
		"contentType": "application/vnd.microsoft.card." + type,
		"content": {
			"autoloop": True,
			"autostart": True,
			"shareable": True,
			"media": [{"profile": "gif", "url": url}],
			"title": title,
			"subtitle": subtitle,
			"text": text,
			"images": images,
			"buttons": buttons
		}
	}

	return card_animation
