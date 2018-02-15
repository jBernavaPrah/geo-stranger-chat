import fbmq as fbmq
import logging
from flask import request
from flask_babel import Babel
from flask_wtf import CSRFProtect
from geolite2 import geolite2
from itsdangerous import TimedJSONWebSignatureSerializer as JWT
from kik import KikApi, Configuration
from mailjet_rest import Client
from telebot import TeleBot

import config
from UniversalBot.BotFrameworkMicrosoft import BotFrameworkMicrosoft

babel = Babel()
geo = geolite2.reader()


@babel.localeselector
def get_locale():
	# need to see if json in request.
	return request.accept_languages.best_match(config.LANGUAGES.keys())


crf_protection = CSRFProtect()
jwt = JWT(config.SECRET_KEY, expires_in=3600)

mailer = Client(auth=(config.MAIL_USERNAME, config.MAIL_PASSWORD), version='v3.1')

if config.KIK_BOT_ENABLED:
	kik_service = KikApi(config.KIK_BOT_USERNAME, config.KIK_BOT_KEY)
	try:
		kik_service.set_configuration(
			Configuration(webhook='https://%s%s' % (config.SERVER_NAME, config.KIK_BOT_WEBHOOK)))
	except Exception as e:
		logging.warning(e)
else:
	kik_service = None

if config.MICROSOFT_BOT_ENABLED:
	microsoft_service = BotFrameworkMicrosoft(config.MICROSOFT_BOT_ID, config.MICROSOFT_BOT_KEY)
else:
	microsoft_service = None

if config.FACEBOOK_BOT_ENABLED:
	facebook_service = fbmq.Page(config.FACEBOOK_BOT_KEY)
	try:
		facebook_service.show_starting_button("START_PAYLOAD")
	except Exception as e:
		logging.warning(e)

else:
	facebook_service = None

if config.TELEGRAM_BOT_ENABLED:
	telegram_service = TeleBot(config.TELEGRAM_BOT_KEY, threaded=False)
	try:
		telegram_service.set_webhook(url='https://%s%s' % (config.SERVER_NAME, config.TELEGRAM_BOT_WEBHOOK), max_connections=100)
	except Exception as e:
		logging.warning(e)
else:
	telegram_service = None

if config.TELEGRAM_STRANGERGEO_ENABLED:
	strangergeo_service = TeleBot(config.TELEGRAM_STRANGERGEO_KEY, threaded=False)
	try:
		strangergeo_service.set_webhook(url='https://%s%s' % (config.SERVER_NAME, config.TELEGRAM_STRANGERGEO_WEBHOOK), max_connections=100)
	except Exception as e:
		logging.warning(e)
else:
	strangergeo_service = None
