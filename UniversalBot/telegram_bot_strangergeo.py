import telebot

import config
from telegram_bot import CustomHandler


class CustomHandler(CustomHandler):
	Type = __name__
	_service = telebot.TeleBot(config.TELEGRAM_STRANGERGEO_KEY, threaded=False)

	def configuration(self):
		self._service.set_webhook(url='https://%s%s' % (config.SERVER_NAME, config.TELEGRAM_STRANGERGEO_WEBHOOK))
