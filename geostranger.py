import logging
from logging.handlers import TimedRotatingFileHandler

from flask import Flask

import config
from controllers.resources.languages import check_language
from log4mongo.handlers import MongoHandler

logging.basicConfig(format=config.LOG_FORMAT, level=logging.INFO)

# formatter = logging.Formatter(config.LOG_FORMAT)

console = logging.StreamHandler()
# console.setLevel(logging.DEBUG)
# console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

db_log = MongoHandler(host=config.DATABASE_HOST, port=config.DATABASE_PORT, database_name=config.LOG_DATABASE_NAME)
# db_log.setLevel(logging.DEBUG)
# db_log.setFormatter(formatter)
logging.getLogger('').addHandler(db_log)

file_log = TimedRotatingFileHandler(config.LOG_FILENAME,
									when="D",
									interval=1,
									backupCount=7)

# file_log.setLevel(logging.DEBUG)
# file_log.setFormatter(formatter)
logging.getLogger('').addHandler(file_log)


def create_app():
	app = Flask(__name__)

	from controllers import index
	app.register_blueprint(index.index_template)
	return app


app = create_app()

# run the app.
if __name__ == "__main__":
	check_language()

	app.run(host='0.0.0.0', port=8080, threaded=True,
			# ssl_context='adhoc'
			)
