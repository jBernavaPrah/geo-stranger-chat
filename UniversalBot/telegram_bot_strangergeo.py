import telebot

import config
from UniversalBot.telegram_bot import Telegram

strangergeo_service = telebot.TeleBot(config.TELEGRAM_STRANGERGEO_KEY, threaded=False)
strangergeo_service.set_webhook(url='https://%s%s' % (config.SERVER_NAME, config.TELEGRAM_STRANGERGEO_WEBHOOK))


class StrangerGeoTelegram(Telegram):
	_service = strangergeo_service
