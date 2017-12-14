from flask.blueprints import Blueprint
from flask_restful import Api
from controllers.resources import TelegramResource

import config

index_template = Blueprint('index', __name__)

@index_template.route('/')
def index_page():
	return 'agc'

index = Api(index_template)
index.add_resource(TelegramResource.Telegram, '/v1/telegram/webhook/%s' % config.TELEGRAM_URL_KEY)
