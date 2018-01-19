import telebot
from flask.blueprints import Blueprint
from flask.globals import request
from flask_restful import Api, Resource

import config
from controllers.resources.GeoStrangerResource import geostranger
from controllers.resources.GeoStrangerTestResource import geostranger_test
from controllers.resources.StrangerGeoResource import strangergeo

index_template = Blueprint('index', __name__)
index = Api(index_template)


# Online
class StrangerGeo(Resource):
	def post(self):
		json_string = request.get_data().decode('utf-8')
		update = telebot.types.Update.de_json(json_string)
		strangergeo.process_new_updates([update])
		return ''


# Online
class GeoStranger(Resource):
	def post(self):
		json_string = request.get_data().decode('utf-8')
		update = telebot.types.Update.de_json(json_string)
		geostranger.process_new_updates([update])
		return ''


# Test
class GeoStrangerTest(Resource):
	def post(self):
		json_string = request.get_data().decode('utf-8')
		update = telebot.types.Update.de_json(json_string)
		geostranger_test.process_new_updates([update])
		return ''


if config.GEOSTRANGER_KEY:
	geostranger_url = '/v1/telegram/geostranger/webhook/%s' % config.TELEGRAM_URL_KEY
	index.add_resource(GeoStranger, geostranger_url)
	geostranger.set_webhook(url='https://%s%s' % (config.SERVER_NAME, geostranger_url))

if config.GEOSTRANGER_TEST_KEY:
	telegram_test_url = '/v1/telegram/geostranger_test/webhook/%s' % config.TELEGRAM_URL_KEY
	index.add_resource(GeoStrangerTest, telegram_test_url)
	geostranger_test.set_webhook(url='https://%s%s' % (config.SERVER_NAME, telegram_test_url))

if config.STRANGERGEO_KEY:
	strangergeo_url = '/v1/telegram/strangergeo/webhook/%s' % config.TELEGRAM_URL_KEY
	index.add_resource(StrangerGeo, strangergeo_url)
	strangergeo.set_webhook(url='https://%s%s' % (config.SERVER_NAME, strangergeo_url))

@index_template.route('/terms')
def terms_page():
	return ''

@index_template.route('/<path:path>')
def index_page(path):
	return 'Site under costruction... ^^'
