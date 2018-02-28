import datetime
import mimetypes

import requests
from flask import request, Blueprint, abort, render_template, redirect, Response, url_for

import config
from UniversalBot.BotFrameworkMicrosoft import WebChatToken
from controllers.helpers import forms
from models import ProxyUrlModel, ConversationModel
from utilities import crf_protection, flasher, geoip

index_template = Blueprint('index', __name__)

if config.TELEGRAM_STRANGERGEO_ENABLED:
	from UniversalBot.telegram_bot_strangergeo import StrangerGeoTelegram


	@index_template.route(config.TELEGRAM_STRANGERGEO_WEBHOOK, methods=['POST'])
	@crf_protection.exempt
	def telegram_strangergeo_webhook():
		StrangerGeoTelegram(request)
		return ''

if config.TELEGRAM_BOT_ENABLED:
	from UniversalBot.telegram_bot import Telegram


	@index_template.route(config.TELEGRAM_BOT_WEBHOOK, methods=['POST'])
	@crf_protection.exempt
	def telegram_webhook():
		Telegram(request)

		return ''

if config.KIK_BOT_ENABLED:
	from UniversalBot.kik_bot import KIK


	@index_template.route(config.KIK_BOT_WEBHOOK, methods=['POST'])
	@crf_protection.exempt
	def kik_webhook():
		KIK(request)
		return ''

if config.VIBER_BOT_ENABLED:
	from UniversalBot.viber_bot import ViberBot


	@index_template.route(config.VIBER_BOT_WEBHOOK, methods=['POST'])
	@crf_protection.exempt
	def viber_webhook():
		ViberBot(request)
		return ''

if config.MICROSOFT_BOT_ENABLED:
	from UniversalBot.microsoft_bot import MicrosoftBot


	@index_template.route(config.MICROSOFT_BOT_WEBHOOK, methods=['POST'])
	@crf_protection.exempt
	def microsoft_webhook():
		# todo check if there are more that one members in addedMembers.
		# https://docs.microsoft.com/en-us/bot-framework/rest-api/bot-framework-rest-connector-activities

		MicrosoftBot(request)

		return ''

if config.FACEBOOK_BOT_ENABLED:

	from UniversalBot.facebook_bot import FacebookBot


	@index_template.route(config.FACEBOOK_BOT_WEBHOOK)
	def facebook_verify():
		# when the endpoint is registered as a webhook, it must echo back
		# the 'hub.challenge' value it receives in the query arguments
		if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
			if not request.args.get("hub.verify_token") == config.FACEBOOK_BOT_TOKEN:
				return "Verification token mismatch", 403
			return request.args["hub.challenge"], 200

		return "Hello world", 200


	@index_template.route(config.FACEBOOK_BOT_WEBHOOK, methods=['POST'])
	@crf_protection.exempt
	def facebook_webhook():
		# if is like! :D
		FacebookBot(request)
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
		return abort(404)

	if proxy.created_at + datetime.timedelta(minutes=60) < datetime.datetime.utcnow():
		# delete the url??
		return abort(404)

	response = requests.get(proxy.url, stream=True, headers=proxy.headers)
	response.raise_for_status()

	_ct = response.headers.get('content-type', proxy.file_type)

	if not _ct.lower().startswith(proxy.file_type):
		_ct = mimetypes.guess_type(proxy.url)[0]

	if not _ct or not _ct.lower().startswith(proxy.file_type):
		_ct = proxy.file_type

	return Response(response.iter_content(chunk_size=10 * 1024), content_type=_ct)


@index_template.route('/')
def index_page():
	# Add new Fake conversation for that ips...

	# todo: TO REMOVE AFTER SOME TIMES
	try:
		geo = geoip()
		if geo:
			longitude = geo.get('location', {}).get('longitude', '')
			latitude = geo.get('location', {}).get('latitude', '')
			country = geo.get('country', {}).get('names', {}).get('en', '')
			continent = geo.get('continent', {}).get('names', {}).get('en', '')

			if longitude and latitude and country and continent:
				conv = ConversationModel()
				conv.conversation_id = '%s%s' % (longitude, latitude)
				conv.chat_type = '_geoip'
				conv.location = [longitude, latitude]
				conv.location_text = country + ', ' + continent
				conv.completed = True
				conv.save()
	except Exception as e:
		# print(e)
		pass

	return render_template('pages/index.html')


@index_template.route('/file/<_id>')
def file_page(_id):
	return redirect(url_for('index.download_action', _id=_id))


@index_template.route('/image/<_id>')
def image_page(_id):
	return redirect(url_for('index.download_action', _id=_id))


@index_template.route('/video/<_id>')
def video_page(_id):
	return redirect(url_for('index.download_action', _id=_id))


@index_template.route('/audio/<_id>')
def audio_page(_id):
	return redirect(url_for('index.download_action', _id=_id))


@index_template.route('/pricing')
def pricing_page():
	return render_template('pages/pricing.html')


@index_template.route('/faq')
def faq_page():
	return render_template('pages/faq.html')


@index_template.route('/contact', methods=['GET', 'POST'])
def contact_page():
	contact_form = forms.ContactForm()
	if contact_form.validate_on_submit():
		contact_form.execute()
		flasher.success('Your message has been sent to us.')
		return redirect(url_for('index.contact_page'))
	flasher.flash_errors(contact_form)
	return render_template('pages/contact.html', contact_form=contact_form)


@index_template.route('/privacy')
def privacy_page():
	return render_template('pages/privacy.html')


@index_template.route('/terms')
def terms_page():
	return render_template('pages/terms.html')


@index_template.route('/webchat')
def webchat_page():
	# Impossible to get user language for now..
	# TODO: Open a issue into github! https://github.com/Microsoft/BotFramework-WebChat/

	# Maybe will work automatically in next months.

	token = WebChatToken(config.WEB_CHAT_IFRAME_KEY).token()
	botname = config.MICROSOFT_BOT_NAME
	username = 'GeoStranger (You)'

	# return render_template('pages/webchat.html', token=token, botname=botname, username=username)

	return redirect(
		'https://webchat.botframework.com/embed/%s?t=%s&username=GeoStranger(You)' % (config.MICROSOFT_BOT_NAME, token),
		302)


@index_template.route('/js/<script>')
def render_script(script):
	return Response(render_template('/js/%s' % script), mimetype='application/javascript')
