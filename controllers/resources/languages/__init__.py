import importlib


def get_lang(lang, what, **kwargs):
	try:
		return getattr(importlib.import_module(lang), what)[0].format(**kwargs)
	except:
		return getattr(importlib.import_module('en'), what)[0].format(**kwargs)


if __name__ == '__main__':
	import en

	def t():
		print '0sdf'

	_what = 'command_start'
	print getattr(en, _what)[0].format(asdf=t)
