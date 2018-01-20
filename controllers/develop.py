from flask import render_template
from flask.blueprints import Blueprint

dev_template = Blueprint('dev', __name__)


@dev_template.route('/<string:page_name>')
def index_page(page_name):
	return render_template('pages/%s.html' % page_name)
