import importlib
import os
import pkgutil


def trans_message(lang, what):
	try:
		x = getattr(importlib.import_module('.' + lang, __name__), what)
		if isinstance(x, tuple):
			x = x[0]
		return x
	except:
		try:
			x = getattr(importlib.import_module('.en', __name__), what)
			if isinstance(x, tuple):
				x = x[0]
			return x
		except:
			return what


def check_language():
	basics = dir(importlib.import_module('.en', __name__))

	pkgpath = os.path.dirname(__file__)
	for _, name, _ in pkgutil.iter_modules([pkgpath]):
		if name == 'en':
			continue

		mod_prop = dir(importlib.import_module('.' + name, __name__))
		diff = list(set(basics) - set(mod_prop))
		if diff:
			print ('Not found in "%s": %s ' % (name, str(diff)))
		diff = list(set(mod_prop) - set(basics))
		if diff:
			print ('Not found in "%s", but found in %s: %s ' % ('en', name, str(diff)))


if __name__ == '__main__':
	def t():
		print ('0sdf')


	_what = 'command_start'
	print (getattr(en, _what)[0].format(asdf=t))
