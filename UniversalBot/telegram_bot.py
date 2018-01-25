import telebot

import config
from telegram_test_bot import CustomHandler


class CustomHandler(CustomHandler):
	_service = telebot.TeleBot(config.TELEGRAM_BOT_KEY, threaded=False)

	def configuration(self):
		self._service.set_webhook(url='https://%s%s' % (config.SERVER_NAME, config.TELEGRAM_BOT_WEBHOOK))
