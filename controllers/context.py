import time
import uuid
from datetime import datetime

from flask import request, redirect, Blueprint, g, abort, make_response
from flask_restful import abort

import config
from UniversalBot.BotFrameworkMicrosoft import WebChatToken
from utilities.flasher import get_flashed_by_categories

context_template = Blueprint('context', __name__)


@context_template.before_app_request
def before_request():
	g.request_start_time = time.time()
	g.request_id = str(uuid.uuid4())

	if request.method == 'OPTIONS':
		response = make_response()
		response.headers['Access-Control-Allow-Origin'] = '*'
		response.headers['Access-Control-Allow-Headers'] = request.headers.get('Access-Control-Request-Headers', '*')
		response.headers['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE'
		return response


@context_template.after_app_request
def after_request(response):
	if g.request_start_time is not None:
		response.headers['X-request-time'] = time.time() - g.request_start_time
	if g.request_id is not None:
		response.headers['X-request-id'] = g.request_id
	response.headers['server'] = 'GeoStranger/Python'

	if request.method != 'OPTIONS':
		response.headers['Access-Control-Allow-Origin'] = '*'
		response.headers['Access-Control-Allow-Headers'] = request.headers.get('Access-Control-Request-Headers', '*')
		response.headers['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE'

	return response


@context_template.before_app_request
def limit_content_length():
	max_length = 3 * 1024 * 1024

	cl = request.content_length
	if cl is not None and cl > max_length:
		abort(413)


@context_template.before_app_request
def before_request():
	# Redirect the www to non www site
	if request.host.startswith('www.'):
		url = request.url.replace('www.', '', 1)
		code = 301
		return redirect(url, code=code)
	# Redirect the not https to https website
	# Also in testing because need to have same functions!
	#
	if request.host is 'geostranger.com' and request.url.startswith('http://'):
		url = request.url.replace('http://', 'https://', 1)
		code = 301
		return redirect(url, code=code)


@context_template.app_context_processor
def utility_processor():
	return dict(get_flashed_by_categories=get_flashed_by_categories)


@context_template.app_context_processor
def utility_processor():
	def is_active(endpoints):
		for endpoint in endpoints:
			if request.endpoint == endpoint:
				return 'active'
		return ''

	return dict(is_active=is_active)


@context_template.app_context_processor
def inject_now():
	return {'now': datetime.utcnow()}


@context_template.app_context_processor
def webchat_iframe():
	def generate_webchat_iframe(style=None):

		style = style or {}

		if not 'height' in style:
			style['height'] = '100%'

		if not 'width' in style:
			style['width'] = '100%'

		token = WebChatToken(config.WEB_CHAT_IFRAME_KEY).token()

		return "<iframe style='height:100%%; width:100%%' src='https://webchat.botframework.com/embed/%s?t=%s'></iframe>" % (
			config.MICROSOFT_BOT_NAME, token)

	return {'webchat_iframe': generate_webchat_iframe}
