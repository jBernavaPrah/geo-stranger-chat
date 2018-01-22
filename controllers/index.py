import telebot
from flask.blueprints import Blueprint
from flask.globals import request
from flask_restful import Api, Resource

import config

index_template = Blueprint('index', __name__)
index = Api(index_template)

if config.STRANGERGEO_ENABLED:
	from controllers.resources.StrangerGeoResource import telegram


	# Online
	class StrangerGeo(Resource):
		def post(self):
			json_string = request.get_data().decode('utf-8')
			update = telebot.types.Update.de_json(json_string)
			telegram.process_new_updates([update])
			return ''


	index.add_resource(StrangerGeo, config.WEBHOOK_STRANGERGEO)

if config.GEOSTRANGER_ENABLED:
	from controllers.resources.GeoStrangerResource import telegram


	# Online
	class GeoStranger(Resource):
		def post(self):
			json_string = request.get_data().decode('utf-8')
			update = telebot.types.Update.de_json(json_string)
			telegram.process_new_updates([update])
			return ''


	index.add_resource(GeoStranger, config.WEBHOOK_GEOSTRANGER)

if config.GEOSTRANGER_TEST_ENABLED:
	from controllers.resources.GeoStrangerTestResource import telegram


	# Test
	class GeoStrangerTest(Resource):
		def post(self):
			json_string = request.get_data().decode('utf-8')
			update = telebot.types.Update.de_json(json_string)
			telegram.process_new_updates([update])
			return ''


	index.add_resource(GeoStrangerTest, config.WEBHOOK_GEOSTRANGER_TEST)


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
