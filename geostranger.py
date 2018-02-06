import logging
from logging.handlers import TimedRotatingFileHandler

from flask import Flask

import config
from controllers import api


def create_app():
	logging.basicConfig(format=config.LOG_FORMAT, level=config.LOG_LEVEL)

	formatter = logging.Formatter(config.LOG_FORMAT)
	file_log = TimedRotatingFileHandler(config.LOG_FILENAME,
										when="D",
										interval=1,
										backupCount=7)

	file_log.setLevel(config.LOG_LEVEL)
	file_log.setFormatter(formatter)
	logging.getLogger('').addHandler(file_log)

	app = Flask(__name__)
	app.logger.addHandler(file_log)

	app.config.from_object(config)

	from controllers import index, develop, context
	app.register_blueprint(context.context_template)
	app.register_blueprint(develop.dev_template, url_prefix="/dev")
	app.register_blueprint(index.index_template)
	app.register_blueprint(api.api_template, **config.SUB_DOMAIN_API)

	from utilities import crf_protection, babel
	crf_protection.init_app(app)
	babel.init_app(app)

	return app


# run the app.
if __name__ == "__main__":
	app = create_app()

	app.run(host='127.0.0.1', port=8443, threaded=True, debug=True, use_reloader=False
			# ssl_context='adhoc'
			)
