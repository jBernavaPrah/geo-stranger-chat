import hashlib
import logging
import os
import socket

from dotenv import load_dotenv

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

load_dotenv(os.path.join(ROOT_DIR, 'geostranger.conf'))

SERVER_HOSTNAME = socket.gethostname()

TELEGRAM_STRANGERGEO_ENABLED = False
TELEGRAM_BOT_ENABLED = False
KIK_BOT_ENABLED = False
MICROSOFT_BOT_ENABLED = False
FACEBOOK_BOT_ENABLED = False
VIBER_BOT_ENABLED = False

if SERVER_HOSTNAME.endswith('geostranger.com'):

	SERVER_NAME = 'geostranger.com'
	DATABASE = 'prod'
	DEBUG = False

	LOG_LEVEL = logging.INFO
	LOG_FORMAT = ' %(asctime)s - ' + SERVER_HOSTNAME + ' - %(levelname)s - %(name)s - %(message)s'
	LOG_FILENAME = '/var/log/geostranger/geostranger.log'
	TELEGRAM_STRANGERGEO_ENABLED = True
	TELEGRAM_BOT_ENABLED = True
	KIK_BOT_ENABLED = True
	MICROSOFT_BOT_ENABLED = True
	FACEBOOK_BOT_ENABLED = True
	VIBER_BOT_ENABLED = False
	SUB_DOMAIN_API = {'subdomain': "api"}

else:
	SERVER_NAME = 'test.geostranger.com'
	DATABASE = 'dev'
	DEBUG = True

	LOG_LEVEL = logging.DEBUG
	LOG_FORMAT = ' %(asctime)s - %(levelname)s - %(name)s - %(message)s'
	LOG_FILENAME = os.path.join(ROOT_DIR, 'log', 'geostranger.log')
	TELEGRAM_STRANGERGEO_ENABLED = False
	TELEGRAM_BOT_ENABLED = True
	KIK_BOT_ENABLED = True
	MICROSOFT_BOT_ENABLED = True
	FACEBOOK_BOT_ENABLED = True
	VIBER_BOT_ENABLED = False
	SUB_DOMAIN_API = {'url_prefix': "/api_test"}

DATABASE_HOST = 'localhost'
DATABASE_PORT = 27017

PREFERRED_URL_SCHEME = 'https'

URL_KEY = os.environ.get('URL_KEY', 'abcdef')

SECRET_KEY = hashlib.md5(os.environ.get('SECRET_KEY', 'we321f3223w1g31234f32wer13qwer123g32sdaf').encode()).hexdigest()

# USE_X_SENDFILE = True

FACEBOOK_BOT_KEY = os.environ.get('FACEBOOK_BOT_KEY',
								  'EAADJI9PXDQIBAL4ZBUV38Gv12gcdILt6G1hO6F0X514Ob8Ajut0opsZAr6nY5yOrvQdUByyAfVvdVX2xshGMPHJ28O35MlYts561iRlH7Gg2D7Kior4oLiwVHEigHEPcJbLPtnBU4aOimDbHFEatHYdv9OaJMDWSAqDxlZAYQZDZD')
FACEBOOK_BOT_WEBHOOK = '/v1/webhook/bot/facebook/webhook/%s' % URL_KEY
FACEBOOK_BOT_TOKEN = os.environ.get('FACEBOOK_BOT_TOKEN', 'sdfkalskflaksjdalskjf')

TELEGRAM_BOT_KEY = os.environ.get('TELEGRAM_BOT_KEY', '484262146:AAEsnvqQb5NRlPI9yn71eRi5sc4ty5M_Lco')
TELEGRAM_BOT_WEBHOOK = '/v1/webhook/bot/telegram/webhook/%s' % URL_KEY

KIK_BOT_WEBHOOK = '/v1/webhook/bot/kik/%s' % URL_KEY
KIK_BOT_USERNAME = os.environ.get('KIK_BOT_USERNAME', 'geostranger')
KIK_BOT_KEY = os.environ.get('KIK_BOT_KEY', '7c565253-fdce-4be4-a10f-87b4099356e6')

TELEGRAM_STRANGERGEO_KEY = os.environ.get('TELEGRAM_STRANGERGEO_KEY')
TELEGRAM_STRANGERGEO_WEBHOOK = '/v1/webhook/bot/telegram/strangergeo/%s' % URL_KEY

MICROSOFT_BOT_NAME = os.environ.get('MICROSOFT_BOT_NAME', 'GeoStranger')
MICROSOFT_BOT_ID = os.environ.get('MICROSOFT_BOT_ID', 'e5c967d0-2f12-4e1e-b971-fc1f177d9f38')
MICROSOFT_BOT_KEY = os.environ.get('MICROSOFT_BOT_KEY', 'dvlolvJJPR91556~){sTQK^')
MICROSOFT_BOT_WEBHOOK = '/v1/webhook/bot/microsoft/%s' % URL_KEY
# MICROSOFT_BOT_WEBHOOK = '/api/messages'


VIBER_BOT_NAME = os.environ.get('VIBER_BOT_NAME', 'GeoStranger')
VIBER_BOT_TOKEN = os.environ.get('VIBER_BOT_TOKEN', '')
VIBER_BOT_WEBHOOK = '/v1/webhook/bot/viber/%s' % URL_KEY

WEB_CHAT_IFRAME_KEY = os.environ.get('WEB_CHAT_IFRAME_KEY',
									 'ddKbtD8p354.cwA.rMo.CHW2H4kUGtHUXUfmobgGG6P4naBpuT4MNkFvbCwn96o')

LANGUAGES = {
	'en': 'English',
	'it': 'Italiano'
}

MAIL_USERNAME = os.environ.get('MAIL_USERNAME', '')
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')
MAIL_SERVER = 'in-v3.mailjet.com'
MAIL_PORT = '588'
MAIL_USE_SSL = False
MAIL_USE_TLS = False

GOOGLE_API_KEY = 'AIzaSyCXc18EdAuOgogqdIoTNdR5YoBq99pa2LA'

#
# MAIL_SERVER : default ‘localhost’
# MAIL_PORT : default 25
# MAIL_USE_TLS : default False
# MAIL_USE_SSL : default False
# MAIL_DEBUG : default app.debug
# MAIL_USERNAME : default None
# MAIL_PASSWORD : default None
# MAIL_DEFAULT_SENDER : default None
# MAIL_MAX_EMAILS : default None
# MAIL_SUPPRESS_SEND : default app.testing
# MAIL_ASCII_ATTACHMENTS : default False
