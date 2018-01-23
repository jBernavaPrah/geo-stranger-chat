import logging
from logging.handlers import TimedRotatingFileHandler

from flask import Flask
from log4mongo import handlers

import config

logging.basicConfig(format=config.LOG_FORMAT, level=logging.DEBUG)

formatter = logging.Formatter(config.LOG_FORMAT)

db_log = handlers.MongoHandler(host=config.DATABASE_HOST, port=config.DATABASE_PORT, collection=config.DATABASE)
db_log.setLevel(logging.DEBUG)
# db_log.setFormatter(formatter)
logging.getLogger('').addHandler(db_log)

file_log = TimedRotatingFileHandler(config.LOG_FILENAME,
									when="D",
									interval=1,
									backupCount=7)

file_log.setLevel(logging.DEBUG)
file_log.setFormatter(formatter)
logging.getLogger('').addHandler(file_log)


def create_app():
	app = Flask(__name__)

	app.config.from_object(config)

	from controllers import index, develop, context
	app.register_blueprint(context.context_template)
	app.register_blueprint(develop.dev_template, url_prefix="/dev")
	app.register_blueprint(index.index_template)

	from utilities import crf_protection
	crf_protection.init_app(app)

	return app


# run the app.
if __name__ == "__main__":
	from controllers.resources.languages import check_language

	check_language()

	app = create_app()

	app.run(host='127.0.0.1', port=8080, threaded=True, debug=True, use_reloader=False
			# ssl_context='adhoc'
			)
