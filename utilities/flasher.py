import flask
from collections import defaultdict


def generic(message, where):
	flask.flash(unicode(message), where)


def info(message):
	flask.flash(unicode(message), 'info')


def success(message):
	flask.flash(unicode(message), 'success')


def warning(message):
	flask.flash(unicode(message), 'warning')


def error(message):
	flask.flash(unicode(message), 'danger')


def get_flashed_by_categories(categories):
	r = defaultdict(list)
	result = flask.get_flashed_messages(with_categories=True, category_filter=categories)
	for categoy, message in result:
		r[categoy].append(message)

	return r


def flash_errors(*forms):
	for form in forms:
		for field, errors in form.errors.items():
			for err in errors:
				error(u"Error in the %s field - %s" % (
					getattr(form, field).label.text,
					err
				))
