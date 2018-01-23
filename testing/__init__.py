sender_class = 'telegram_test'

mod = __import__('UniversalBot.%s' % sender_class, fromlist=['CustomHandler'])
klass = getattr(mod, 'CustomHandler')()
klass.send_text()
