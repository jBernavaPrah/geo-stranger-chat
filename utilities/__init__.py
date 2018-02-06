from flask import request
from flask_wtf import CSRFProtect
from itsdangerous import TimedJSONWebSignatureSerializer as JWT

import config

from flask_babel import Babel

babel = Babel()


@babel.localeselector
def get_locale():
	# need to see if json in request.
	return request.accept_languages.best_match(config.LANGUAGES.keys())


crf_protection = CSRFProtect()
jwt = JWT(config.SECRET_KEY, expires_in=3600)
