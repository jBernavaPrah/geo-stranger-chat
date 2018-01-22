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
	STRANGERGEO_ENABLED = True
	GEOSTRANGER_TEST_ENABLED = False
	GEOSTRANGER_ENABLED = True


else:
	SERVER_NAME = 'f691193f.ngrok.io'
	DATABASE = 'dev'
	DEBUG = True
	SECRET_KEY = 'we321f3223w1g31234f32wer13qwer123g32sdaf'

	DATABASE_HOST = 'localhost'
	DATABASE_PORT = 27017
	LOG_FORMAT = ' %(asctime)s - %(levelname)s - %(name)s - %(message)s'
	LOG_FILENAME = os.path.join(ROOT_DIR, 'log', 'uploaderjs.log')
	STRANGERGEO_ENABLED = False
	GEOSTRANGER_TEST_ENABLED = True
	GEOSTRANGER_ENABLED = False

TELEGRAM_URL_KEY = os.environ.get('T_URL_KEY', 'abcdef')

# USE_X_SENDFILE = True
GEOSTRANGER_TEST_KEY = '484262146:AAEsnvqQb5NRlPI9yn71eRi5sc4ty5M_Lco'
WEBHOOK_GEOSTRANGER_TEST = '/v1/telegram/geostranger_test/webhook/%s' % TELEGRAM_URL_KEY
GEOSTRANGER_KEY = os.environ.get('GS_KEY', )
WEBHOOK_GEOSTRANGER = '/v1/telegram/geostranger/webhook/%s' % TELEGRAM_URL_KEY
STRANGERGEO_KEY = os.environ.get('SG_KEY')
WEBHOOK_STRANGERGEO = '/v1/telegram/strangergeo/webhook/%s' % TELEGRAM_URL_KEY
