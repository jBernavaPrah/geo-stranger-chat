import telebot
from flask.blueprints import Blueprint
from flask.globals import request
from flask_restful import Api, Resource

import config
from UniversalBot.telegram_test_bot import CustomHandler as TelegramTestHandler
from UniversalBot.telegram_bot import CustomHandler as TelegramHandler
from utilities import crf_protection

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
		telegram_handler.process(request)
		return ''


if config.TELEGRAM_BOT_TEST_ENABLED:
	telegram_test_handler = TelegramTestHandler(True)


	@index_template.route(config.TELEGRAM_TEST_BOT_WEBHOOK, methods=['POST'])
	@crf_protection.exempt
	def webhook_telegram_test():
		telegram_test_handler.process(request)
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
