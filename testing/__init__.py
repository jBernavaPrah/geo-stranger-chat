import importlib


def xx(what):
	mod = importlib.import_module('UniversalBot')
	return getattr(mod, what)()


x = xx('KIK')
print(x.__class__.__name__)
