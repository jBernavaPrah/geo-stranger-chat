import requests
from flask import request, Blueprint, abort, render_template, redirect, Response, url_for

import config

from models import ProxyUrlModel

from utilities import crf_protection

index_template = Blueprint('index', __name__)

if config.TELEGRAM_STRANGERGEO_ENABLED:
	from UniversalBot.telegram_bot_strangergeo import StrangerGeoTelegram


	@index_template.route(config.TELEGRAM_STRANGERGEO_WEBHOOK, methods=['POST'])
	@crf_protection.exempt
	def telegram_strangergeo_webhook():
		StrangerGeoTelegram(request.get_data().decode('utf-8'))
		return ''

if config.TELEGRAM_BOT_ENABLED:
	from UniversalBot.telegram_bot import Telegram


	@index_template.route(config.TELEGRAM_BOT_WEBHOOK, methods=['POST'])
	@crf_protection.exempt
	def telegram_webhook():
		Telegram(request.get_data().decode('utf-8'))

		return ''

if config.KIK_BOT_ENABLED:
	from UniversalBot.kik_bot import KIK


	@index_template.route(config.KIK_BOT_WEBHOOK, methods=['POST'])
	@crf_protection.exempt
	def kik_webhook():
		KIK(request.json['messages'])
		return ''

if config.MICROSOFT_BOT_ENABLED:

	from UniversalBot.skype_bot import Skype
	from UniversalBot.webchat_bot import WebChat


	@index_template.route(config.MICROSOFT_BOT_WEBHOOK, methods=['POST'])
	@crf_protection.exempt
	def skype_test_webhook():

		data = request.json

		# todo check if there are more that one members in addedMembers.
		# https://docs.microsoft.com/en-us/bot-framework/rest-api/bot-framework-rest-connector-activities

		if 'channelId' in data and data['channelId'] == 'webchat':
			WebChat(data)

		if 'channelId' in data and data['channelId'] == 'skype':
			Skype(data)

		return ''


@index_template.route('/<_id>', subdomain='r')
def redirect_action(_id):
	redirect_to = ProxyUrlModel.objects(id=str(_id)).modify(inc__opened_times=1)

	if not redirect_to:
		abort(406)

	return redirect(redirect_to.url, code=301)


@index_template.route('/download/<_id>')
def download_action(_id):
	proxy = ProxyUrlModel.objects(id=str(_id)).first()
	if not proxy:
		abort(406)

	response = requests.get(proxy.url, stream=True)
	response.raise_for_status()

	return Response(response.iter_content(chunk_size=10 * 1024), content_type=response.headers['Content-Type'])


@index_template.route('/')
def index_page():
	return render_template('pages/index.html')


@index_template.route('/video/<_id>')
def video_page(_id):
	redirect(url_for('index.download_action', _id=_id))


@index_template.route('/audio/<_id>')
def audio_page(_id):
	redirect(url_for('index.download_action', _id=_id))


@index_template.route('/pricing')
def pricing_page():
	return render_template('pages/pricing.html')


@index_template.route('/faq')
def faq_page():
	return render_template('pages/faq.html')


@index_template.route('/contact')
def contact_page():
	return render_template('pages/contact.html')


@index_template.route('/privacy')
def privacy_page():
	return render_template('pages/privacy.html')


@index_template.route('/terms')
def terms_page():
	return render_template('pages/terms.html')


@index_template.route('/webchat')
def webchat_page():
	return render_template('pages/webchat.html')
