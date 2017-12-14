import logging
from flask import Flask

import config

logging.basicConfig(filename=config.LOG_FILENAME, filemode='w', level=logging.DEBUG)

logging.getLogger().addHandler(logging.StreamHandler())


def create_app():
	app = Flask(__name__)

	from controllers import index
	app.register_blueprint(index.index_template)
	return app


app  = create_app()

# application.register_blueprint(task.task_template, url_prefix='/task')


# run the app.
if __name__ == "__main__":
	app.run(host='0.0.0.0', port=8080, threaded=True,
					# ssl_context='adhoc'
					)
