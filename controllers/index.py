import telebot
from flask.blueprints import Blueprint
from flask.globals import request
from flask_restful import Api, Resource

import config
from controllers.resources.GeoStrangerResource import telegram as telegram_online
from controllers.resources.GeoStrangerTestResource import telegram as telegram_test
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
		telegram_online.process_new_updates([update])
		return ''


# Test
class GeoStrangerTest(Resource):
	def post(self):
		json_string = request.get_data().decode('utf-8')
		update = telebot.types.Update.de_json(json_string)
		telegram_test.process_new_updates([update])
		return ''


if config.GEOSTRANGER_KEY:
	geostranger_url = '/v1/telegram/geostranger/webhook/%s' % config.TELEGRAM_URL_KEY
	index.add_resource(GeoStranger, geostranger_url)
	if hasattr(config, 'SERVER_NAME'):
		telegram_online.set_webhook(url='https://%s%s' % (config.SERVER_NAME, geostranger_url))

if config.GEOSTRANGER_TEST_KEY:
	telegram_test_url = '/v1/telegram/geostranger_test/webhook/%s' % config.TELEGRAM_URL_KEY
	index.add_resource(GeoStrangerTest, telegram_test_url)
	if hasattr(config, 'SERVER_NAME'):
		telegram_test.set_webhook(url='https://%s%s' % (config.SERVER_NAME, telegram_test_url))

if config.STRANGERGEO_KEY:
	strangergeo_url = '/v1/telegram/strangergeo/webhook/%s' % config.TELEGRAM_URL_KEY
	index.add_resource(StrangerGeo, strangergeo_url)
	if hasattr(config, 'SERVER_NAME'):
		strangergeo.set_webhook(url='https://%s%s' % (config.SERVER_NAME, strangergeo_url))


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
