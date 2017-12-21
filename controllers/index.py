import telebot
from flask.blueprints import Blueprint
from flask.globals import request
from flask_restful import Api, Resource

import config
from controllers.resources.TelegramItResource import telegram_it
from models import Logging

index_template = Blueprint('index', __name__)
index = Api(index_template)


# Italian
class TelegramIt(Resource):
	def post(self):
		json_string = request.get_data().decode('utf-8')
		Logging(raw=request.json).save()

		update = telebot.types.Update.de_json(json_string)
		telegram_it.process_new_updates([update])
		return ''


telegram_it_url = '/v1/telegram/it/webhook/%s' % config.TELEGRAM_URL_KEY
index.add_resource(TelegramIt, telegram_it_url)
telegram_it.set_webhook(url='https://%s%s' % (config.SERVER_NAME, telegram_it_url))



@index_template.route('/<path:path>')
def index_page(path):
	return 'Site under costruction... ^^'
