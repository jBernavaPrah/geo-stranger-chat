import os
import socket

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

SERVER_HOSTNAME = socket.gethostname()

if SERVER_HOSTNAME.endswith('geostranger.com'):
	SERVER_NAME = 'geostranger.com'
	DATABASE = 'prod'
	DEBUG = False
	SECRET_KEY = os.environ.get('SECRET_KEY')
	DATABASE_HOST = '10.10.45.169'
	DATABASE_PORT = 27017
	LOG_FORMAT = ' %(asctime)s - ' + SERVER_HOSTNAME + ' - %(levelname)s - %(name)s - %(message)s'
	LOG_FILENAME = '/var/log/geostranger/uploaderjs.log'
	TELEGRAM_STRANGERGEO_ENABLED = True
	TELEGRAM_BOT_TEST_ENABLED = False
	TELEGRAM_BOT_ENABLED = True
	KIK_BOT_ENABLED = True
	KIK_TEST_BOT_ENABLED = False



else:
	SERVER_NAME = 'f6cb221b.ngrok.io'
	DATABASE = 'dev'
	DEBUG = True
	SECRET_KEY = 'we321f3223w1g31234f32wer13qwer123g32sdaf'

	DATABASE_HOST = 'localhost'
	DATABASE_PORT = 27017
	LOG_FORMAT = ' %(asctime)s - %(levelname)s - %(name)s - %(message)s'
	LOG_FILENAME = os.path.join(ROOT_DIR, 'log', 'uploaderjs.log')
	TELEGRAM_STRANGERGEO_ENABLED = False
	TELEGRAM_BOT_TEST_ENABLED = True
	TELEGRAM_BOT_ENABLED = False
	KIK_BOT_ENABLED = False
	KIK_TEST_BOT_ENABLED = True

URL_KEY = os.environ.get('URL_KEY', 'abcdef')

# USE_X_SENDFILE = True
TELEGRAM_TEST_BOT_KEY = '484262146:AAEsnvqQb5NRlPI9yn71eRi5sc4ty5M_Lco'
TELEGRAM_TEST_BOT_WEBHOOK = '/v1/telegram/geostranger_test/webhook/%s' % URL_KEY
TELEGRAM_BOT_KEY = os.environ.get('TELEGRAM_BOT_KEY', )
TELEGRAM_BOT_WEBHOOK = '/v1/telegram/geostranger/webhook/%s' % URL_KEY

KIK_BOT_WEBHOOK = '/v1/kik/geostranger/webhook/%s' % URL_KEY
KIK_BOT_USERNAME = 'geostrangerbot'
KIK_BOT_API_KEY = os.environ.get('KIK_BOT_KEY', )

KIK_TEST_BOT_WEBHOOK = '/v1/kik/geostrangerbot/webhook/%s' % URL_KEY
KIK_TEST_BOT_USERNAME = 'geostranger'
KIK_TEST_BOT_API_KEY = '7c565253-fdce-4be4-a10f-87b4099356e6'

STRANGERGEO_KEY = os.environ.get('STRANGERGEO_KEY')
WEBHOOK_STRANGERGEO = '/v1/telegram/strangergeo/webhook/%s' % URL_KEY
