import telebot

from flask import request, Blueprint, abort, send_file, make_response
from flask_restful import Api, Resource
from itsdangerous import SignatureExpired

import config
from UniversalBot.telegram_test_bot import CustomHandler as TelegramTestHandler
from UniversalBot.telegram_bot import CustomHandler as TelegramHandler
from UniversalBot.kik_test_bot import CustomHandler as KikTestHandler
from UniversalBot.kik_bot import CustomHandler as KikHandler
from models import FileModel
from utilities import crf_protection, jwt

index_template = Blueprint('index', __name__)
index = Api(index_template)

if config.TELEGRAM_STRANGERGEO_ENABLED:
	from controllers.resources.StrangerGeoResource import telegram


	# Online
	class StrangerGeo(Resource):
		def post(self):
			json_string = request.get_data().decode('utf-8')
			update = telebot.types.Update.de_json(json_string)
			telegram.process_new_updates([update])
			return ''


	index.add_resource(StrangerGeo, config.WEBHOOK_STRANGERGEO)

if config.TELEGRAM_BOT_ENABLED:
	telegram_handler = TelegramHandler(True)


	@index_template.route(config.TELEGRAM_BOT_WEBHOOK, methods=['POST'])
	@crf_protection.exempt
	def webhook_telegram():
		return telegram_handler.process(request)

if config.TELEGRAM_BOT_TEST_ENABLED:
	telegram_test_handler = TelegramTestHandler(True)


	@index_template.route(config.TELEGRAM_TEST_BOT_WEBHOOK, methods=['POST'])
	@crf_protection.exempt
	def webhook_telegram_test():
		return telegram_test_handler.process(request)

if config.KIK_TEST_BOT_ENABLED:
	kik_test_handler = KikTestHandler(True)


	@index_template.route(config.KIK_TEST_BOT_WEBHOOK, methods=['POST'])
	@crf_protection.exempt
	def webhook_kik_test():
		return kik_test_handler.process(request)

if config.KIK_BOT_ENABLED:
	kik_handler = KikHandler(True)


	@index_template.route(config.KIK_BOT_WEBHOOK, methods=['POST'])
	@crf_protection.exempt
	def webhook_kik():
		return kik_handler.process(request)


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
	return 'Site under costruction... ^^'


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
