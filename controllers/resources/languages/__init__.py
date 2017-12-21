import importlib
import os
import pkgutil


def get_lang(lang, what, **kwargs):
	try:
		return getattr(importlib.import_module('en' + lang, __name__), what)[0].format(**kwargs)
	except:
		return getattr(importlib.import_module('.en', __name__), what)[0].format(**kwargs)


def check_language():
	basics = dir(importlib.import_module('.en', __name__))

	pkgpath = os.path.dirname(__file__)
	for _, name, _ in pkgutil.iter_modules([pkgpath]):
		if name == 'en':
			continue

		mod_prop = dir(importlib.import_module('.' + name, __name__))
		diff = list(set(basics) - set(mod_prop))
		if diff:
			print 'Not found in %s: %s ' % (name, str(diff))
		diff = list(set(mod_prop) - set(basics))
		if diff:
			print 'Not found in %s, but found in %s: %s ' % ('en', name, str(diff))


if __name__ == '__main__':
	def t():
		print '0sdf'


	_what = 'command_start'
	print getattr(en, _what)[0].format(asdf=t)
