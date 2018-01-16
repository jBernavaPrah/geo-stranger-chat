import os
import socket

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

if socket.gethostname().endswith('geostranger.com'):
	SERVER_NAME = 'geostranger.com'
	DATABASE = 'prod'
	DEBUG = False
	SECRET_KEY = os.environ.get('SECRET_KEY')


else:
	SERVER_NAME = '540deb51.ngrok.io'
	DATABASE = 'dev'
	DEBUG = True
	SECRET_KEY = 'we321f3223w1g31234f32wer13qwer123g32sdaf'


GEOSTRANGER_TEST_KEY = '484262146:AAEsnvqQb5NRlPI9yn71eRi5sc4ty5M_Lco'
TELEGRAM_URL_KEY = os.environ.get('T_URL_KEY')
GEOSTRANGER_KEY = os.environ.get('GS_KEY')
STRANGERGEO_KEY = os.environ.get('SG_KEY')

LOG_FILENAME = os.path.join(ROOT_DIR, 'log', 'uploaderjs.log')
