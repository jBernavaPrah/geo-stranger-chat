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

if SERVER_HOSTNAME.endswith('geostranger.com'):

	SERVER_NAME = 'geostranger.com'
	DATABASE = 'prod'
	DEBUG = False

	DATABASE_HOST = '10.10.45.169'
	DATABASE_PORT = 27017
	LOG_LEVEL = logging.INFO
	LOG_FORMAT = ' %(asctime)s - ' + SERVER_HOSTNAME + ' - %(levelname)s - %(name)s - %(message)s'
	LOG_FILENAME = '/var/log/geostranger/geostranger.log'
	TELEGRAM_STRANGERGEO_ENABLED = True
	TELEGRAM_BOT_ENABLED = True
	KIK_BOT_ENABLED = True
	MICROSOFT_BOT_ENABLED = True
	SUB_DOMAIN_API = {'subdomain': "api"}

else:
	SERVER_NAME = 'test.geostranger.com'
	DATABASE = 'dev'
	DEBUG = True

	DATABASE_HOST = 'localhost'
	DATABASE_PORT = 27017
	LOG_LEVEL = logging.DEBUG
	LOG_FORMAT = ' %(asctime)s - %(levelname)s - %(name)s - %(message)s'
	LOG_FILENAME = os.path.join(ROOT_DIR, 'log', 'geostranger.log')
	TELEGRAM_STRANGERGEO_ENABLED = False
	TELEGRAM_BOT_ENABLED = True
	KIK_BOT_ENABLED = True
	MICROSOFT_BOT_ENABLED = True
	SUB_DOMAIN_API = {'url_prefix': "/api_test"}

PREFERRED_URL_SCHEME = 'https'

URL_KEY = os.environ.get('URL_KEY', 'abcdef')

SECRET_KEY = hashlib.md5(os.environ.get('SECRET_KEY', 'we321f3223w1g31234f32wer13qwer123g32sdaf').encode()).hexdigest()

# USE_X_SENDFILE = True

TELEGRAM_BOT_KEY = os.environ.get('TELEGRAM_BOT_KEY', '484262146:AAEsnvqQb5NRlPI9yn71eRi5sc4ty5M_Lco')
TELEGRAM_BOT_WEBHOOK = '/v1/webhook/bot/telegram/webhook/%s' % URL_KEY

KIK_BOT_WEBHOOK = '/v1/webhook/bot/kik/%s' % URL_KEY
KIK_BOT_USERNAME = os.environ.get('KIK_BOT_USERNAME', 'geostranger')
KIK_BOT_KEY = os.environ.get('KIK_BOT_KEY', '7c565253-fdce-4be4-a10f-87b4099356e6')

TELEGRAM_STRANGERGEO_KEY = os.environ.get('TELEGRAM_STRANGERGEO_KEY')
TELEGRAM_STRANGERGEO_WEBHOOK = '/v1/webhook/bot/telegram/strangergeo/%s' % URL_KEY

MICROSOFT_BOT_NAME = 'GeoStranger'
MICROSOFT_BOT_ID = os.environ.get('MICROSOFT_BOT_ID', 'e5c967d0-2f12-4e1e-b971-fc1f177d9f38')
MICROSOFT_BOT_KEY = os.environ.get('MICROSOFT_BOT_KEY', 'dvlolvJJPR91556~){sTQK^')
MICROSOFT_BOT_WEBHOOK = '/v1/webhook/bot/microsoft/%s' % URL_KEY
# MICROSOFT_BOT_WEBHOOK = '/api/messages'

WEB_CHAT_IFRAME_KEY = os.environ.get('WEB_CHAT_IFRAME_KEY',
									 'ddKbtD8p354.cwA.rMo.CHW2H4kUGtHUXUfmobgGG6P4naBpuT4MNkFvbCwn96o')
