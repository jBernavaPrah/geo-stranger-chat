import telebot
from flask.blueprints import Blueprint
from flask.globals import request
from flask_restful import Api, Resource

import config
from controllers.resources.TelegramResource import telegram_online
from controllers.resources.TelegramTestResource import telegram_test
from models import LoggingModel

index_template = Blueprint('index', __name__)
index = Api(index_template)


# Online
class TelegramOnline(Resource):
	def post(self):
		json_string = request.get_data().decode('utf-8')
		LoggingModel(raw=request.json).save()

		update = telebot.types.Update.de_json(json_string)
		telegram_online.process_new_updates([update])
		return ''


# Test
class TelegramTest(Resource):
	def post(self):
		json_string = request.get_data().decode('utf-8')
		LoggingModel(raw=request.json).save()

		update = telebot.types.Update.de_json(json_string)
		telegram_test.process_new_updates([update])
		return ''


telegram_online_url = '/v1/telegram/webhook/%s' % config.TELEGRAM_URL_KEY
index.add_resource(TelegramOnline, telegram_online_url)
telegram_online.set_webhook(url='https://%s%s' % (config.SERVER_NAME, telegram_online_url))

telegram_test_url = '/v1/telegram/test/webhook/%s' % config.TELEGRAM_URL_KEY
index.add_resource(TelegramTest, telegram_test_url)
telegram_test.set_webhook(url='https://%s%s' % (config.SERVER_NAME, telegram_test_url))

@index_template.route('/<path:path>')
def index_page(path):
	return 'Site under costruction... ^^'
