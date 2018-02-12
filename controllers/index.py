import requests
from flask import request, Blueprint, abort, render_template, redirect, Response, url_for, make_response


import config
from UniversalBot.BotFrameworkMicrosoft import WebChatToken
from controllers.helpers import forms

from models import ProxyUrlModel

from utilities import crf_protection, flasher,  mailer
from utilities.flasher import flash_errors
from utilities.mailer import send_mail_to_admin

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

if config.MICROSOFT_BOT_ENABLED:
	from UniversalBot.microsoft_bot import MicrosoftBot


	@index_template.route(config.MICROSOFT_BOT_WEBHOOK, methods=['POST'])
	@crf_protection.exempt
	def microsoft_webhook():
		# todo check if there are more that one members in addedMembers.
		# https://docs.microsoft.com/en-us/bot-framework/rest-api/bot-framework-rest-connector-activities

		MicrosoftBot(request)

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


@index_template.route('/contact', methods=['GET', 'POST'])
def contact_page():
	contact_form = forms.ContactForm()
	if contact_form.validate_on_submit():
		contact_form.execute()
		flasher.success('Your message has been sent to us.')
		return redirect(url_for('index.contact_page'))
	flash_errors(contact_form)
	return render_template('pages/contact.html', contact_form=contact_form)


@index_template.route('/test_mail')
def test_page():
	send_mail_to_admin(template='contact_us', fill_with=dict(EMAIL='test',
															 SUBJECT='test2',
															 MESSAGE='test3')
					   )

	return ''


@index_template.route('/privacy')
def privacy_page():
	return render_template('pages/privacy.html')


@index_template.route('/terms')
def terms_page():
	return render_template('pages/terms.html')


@index_template.route('/webchat')
def webchat_page():
	token = WebChatToken(config.WEB_CHAT_IFRAME_KEY).token()

	return redirect(
		'https://webchat.botframework.com/embed/%s?t=%s&username=GeoStranger(You)' % (config.MICROSOFT_BOT_NAME, token),
		302)


@index_template.route('/js/<script>')
def render_script(script):
	return Response(render_template('/js/%s' % script), mimetype='application/javascript')
