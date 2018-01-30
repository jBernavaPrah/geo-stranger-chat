import logging
from flask import request, Blueprint, abort, send_file, make_response
from flask_restful import Api
from itsdangerous import SignatureExpired

import config

from UniversalBot.telegram_bot import CustomHandler as TelegramHandler

from UniversalBot.kik_bot import CustomHandler as KikHandler
from UniversalBot.telegram_bot_strangergeo import CustomHandler as TelegramStrangerGeoHandler

from UniversalBot.skype_bot import CustomHandler as SkypeHandler
from UniversalBot.webchat_bot import CustomHandler as WebChatHandler

from models import FileModel
from utilities import crf_protection, jwt

index_template = Blueprint('index', __name__)
index = Api(index_template)

if config.TELEGRAM_STRANGERGEO_ENABLED:
	logging.info('Telegram StrangerGeo Enabled')
	telegram_strangergeo_handler = TelegramStrangerGeoHandler(True)


	@index_template.route(config.TELEGRAM_STRANGERGEO_WEBHOOK, methods=['POST'])
	@crf_protection.exempt
	def telegram_strangergeo_webhook():
		return telegram_strangergeo_handler.process(request)

if config.TELEGRAM_BOT_ENABLED:
	telegram_handler = TelegramHandler(True)


	@index_template.route(config.TELEGRAM_BOT_WEBHOOK, methods=['POST'])
	@crf_protection.exempt
	def telegram_webhook():
		telegram_handler.process(request)
		return ''

if config.KIK_BOT_ENABLED:
	kik_handler = KikHandler(True)


	@index_template.route(config.KIK_BOT_WEBHOOK, methods=['POST'])
	@crf_protection.exempt
	def kik_webhook():
		kik_handler.process(request)
		return ''

if config.MICROSOFT_BOT_ENABLED:

	skype_handler = SkypeHandler(True)
	webchat_handler = WebChatHandler(True)


	@index_template.route(config.MICROSOFT_BOT_WEBHOOK, methods=['POST'])
	@crf_protection.exempt
	def skype_test_webhook():

		data = request.json

		if 'type' in data and data['type'] == 'deleteUserData':
			return ''

		if 'type' in data and data['type'] == 'ping':
			return ''

		if 'type' in data and (data['type'] == 'message' or data['type'] == 'conversationUpdate'):

			if 'membersAdded' in data:
				for m in data['membersAdded']:
					if not m['id'].startswith(config.MICROSOFT_BOT_NAME):
						return ''

			# todo check if there are more that one members in addedMembers.
			# https://docs.microsoft.com/en-us/bot-framework/rest-api/bot-framework-rest-connector-activities

			if 'channelId' in data and data['channelId'] == 'webchat':
				webchat_handler.process(request)

			if 'channelId' in data and data['channelId'] == 'skype':
				skype_handler.process(request)

		return ''


@index_template.route('/download/<token>')
def download_file(token):
	try:
		file_id = jwt.loads(token)
	except SignatureExpired:
		return abort(403)
	except Exception:
		return abort(401)

	_f = FileModel.objects(id=file_id).first()

	if not _f:
		return abort(404)

	try:

		response = make_response(send_file(_f.file, mimetype=_f.file.content_type))
		response.headers['Content-Length'] = _f.file.length
		return response

	except Exception as e:
		return abort(505)


@index_template.route('/video-player/<token>')
def play_video(token):
	return ''


@index_template.route('/audio-player/<token>')
def play_audio(token):
	return ''


@index_template.route('/')
def index_page():
	return 'Site under costruction... :P ^^'


@index_template.route('/<path:path>')
def other_page(path):
	return 'Site under costruction... ^^'


@index_template.route('/pricing')
def pricing_page():
	return ''


@index_template.route('/faq')
def faq_page():
	return ''


@index_template.route('/contact')
def contact_page():
	return ''


@index_template.route('/privacy')
def privacy_page():
	return ''


@index_template.route('/terms')
def terms_page():
	return ''
