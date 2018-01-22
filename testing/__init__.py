class test():
	def c(self):
		raise NotImplemented


class t2(object):
	__metaclass__ = test


x = t2()

print callable(getattr(x, 'c'))
