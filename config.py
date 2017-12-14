import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# SERVER_NAME = os.environ.get('SERVER_NAME', 'iqggvgbnec.localtunnel.me')
# SERVER_NAME = os.environ.get('SERVER_NAME', 'geo.local:8080')
SERVER_NAME = os.environ.get('SERVER_NAME', 'ee2448a6.ngrok.io')

DEBUG = bool(os.environ.get('DEBUG', True))

AWS_KEY_ID = os.environ.get('AWS_KEY_ID', None)
AWS_SECRET = os.environ.get('AWS_SECRET', None)
REGION_NAME = os.environ.get('REGION_NAME', None)

SECRET_KEY = os.environ.get('SECRET_KEY', 'we321f3223w1g31234f32wer13qwer123g32sdaf')

TELEGRAM_KEY = os.environ.get('TELEGRAM_KEY', '484262146:AAEsnvqQb5NRlPI9yn71eRi5sc4ty5M_Lco')
TELEGRAM_URL_KEY = os.environ.get('TELEGRAM_URL_KEY', 'SA3D2F1A3S1F353W43513ASD2F13X2V1')

LOG_FILENAME = os.environ.get('LOG_FILENAME', os.path.join(ROOT_DIR, 'log', 'uploaderjs.log'))

# redis:

redis_host = os.environ.get('REDIS_HOST', 'localhost')

