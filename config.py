import os
import socket

import logging
from logging.handlers import TimedRotatingFileHandler

from flask import Flask
from log4mongo import handlers

from controllers import develop

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

	GEOSTRANGER_TEST_KEY = None


else:
	SERVER_NAME = 'f691193f.ngrok.io'
	DATABASE = 'dev'
	DEBUG = True
	SECRET_KEY = 'we321f3223w1g31234f32wer13qwer123g32sdaf'
	GEOSTRANGER_TEST_KEY = '484262146:AAEsnvqQb5NRlPI9yn71eRi5sc4ty5M_Lco'
	DATABASE_HOST = 'localhost'
	DATABASE_PORT = 27017
	LOG_FORMAT = ' %(asctime)s - %(levelname)s - %(name)s - %(message)s'
	LOG_FILENAME = os.path.join(ROOT_DIR, 'log', 'uploaderjs.log')

TELEGRAM_URL_KEY = os.environ.get('T_URL_KEY', 'abcdef')
GEOSTRANGER_KEY = os.environ.get('GS_KEY', )
STRANGERGEO_KEY = os.environ.get('SG_KEY')




def create_app():
	app = Flask(__name__)

	from controllers import index
	app.register_blueprint(develop.dev_template, url_prefix="/dev")
	app.register_blueprint(index.index_template)

	return app

def configure_logger():
	logging.basicConfig(format=LOG_FORMAT, level=logging.DEBUG)

	formatter = logging.Formatter(LOG_FORMAT)

	db_log = handlers.MongoHandler(host=DATABASE_HOST, port=DATABASE_PORT, collection=DATABASE)
	db_log.setLevel(logging.DEBUG)
	# db_log.setFormatter(formatter)
	logging.getLogger('').addHandler(db_log)

	file_log = TimedRotatingFileHandler(LOG_FILENAME,
										when="D",
										interval=1,
										backupCount=7)

	file_log.setLevel(logging.DEBUG)
	file_log.setFormatter(formatter)
	logging.getLogger('').addHandler(file_log)
