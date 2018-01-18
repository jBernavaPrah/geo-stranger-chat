import os
import socket

import logging

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

SERVER_HOSTNAME = socket.gethostname()

if SERVER_HOSTNAME.endswith('geostranger.com'):
	SERVER_NAME = 'geostranger.com'
	DATABASE = 'prod'
	DEBUG = False
	SECRET_KEY = os.environ.get('SECRET_KEY')
	DATABASE_HOST = '10.10.45.169'
	DATABASE_PORT = 27017
	LOG_DATABASE_NAME = 'Production_log'
	LOG_FORMAT = SERVER_HOSTNAME + ' %(asctime)s:' + logging.BASIC_FORMAT

	GEOSTRANGER_TEST_KEY = None


else:
	SERVER_NAME = '540deb51.ngrok.io'
	DATABASE = 'dev'
	DEBUG = True
	SECRET_KEY = 'we321f3223w1g31234f32wer13qwer123g32sdaf'
	GEOSTRANGER_TEST_KEY = '484262146:AAEsnvqQb5NRlPI9yn71eRi5sc4ty5M_Lco'
	DATABASE_HOST = 'localhost'
	DATABASE_PORT = 27017
	LOG_DATABASE_NAME = 'Dev_log'
	LOG_FORMAT = SERVER_HOSTNAME + ' %(asctime)s:' + logging.BASIC_FORMAT

TELEGRAM_URL_KEY = os.environ.get('T_URL_KEY', 'abcdef')
GEOSTRANGER_KEY = os.environ.get('GS_KEY', )
STRANGERGEO_KEY = os.environ.get('SG_KEY')

LOG_FILENAME = os.path.join(ROOT_DIR, 'log', 'uploaderjs.log')
