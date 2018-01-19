from flask.blueprints import Blueprint

dev_template = Blueprint('dev', __name__)

@dev_template.route('/index')
def index_page():
	return 'dev page'
