import logging

from flask import Flask

import config
from controllers.resources.languages import check_language
from log4mongo.handlers import MongoHandler

logging.basicConfig(filename=config.LOG_FILENAME, filemode='w', level=logging.DEBUG)

logger = logging.getLogger()

logger.addHandler(logging.StreamHandler())
logger.addHandler(MongoHandler(host='localhost'))


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
