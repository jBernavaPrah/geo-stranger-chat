from flask_wtf import CSRFProtect
from itsdangerous import TimedJSONWebSignatureSerializer as JWT

import base64

import config

crf_protection = CSRFProtect()
jwt = JWT(config.SECRET_KEY, expires_in=3600)


