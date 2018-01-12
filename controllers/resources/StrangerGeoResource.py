# coding=utf-8
import telebot
import config
from controllers.resources.telegram_base import reply_to_message

strangergeo = telebot.TeleBot(config.STRANGERGEO_KEY, threaded=False)


@strangergeo.message_handler(func=lambda message: True,
							 content_types=['audio', 'video', 'document', 'text', 'location', 'contact', 'sticker'])
def echo_all(message):
	reply_to_message(strangergeo, message, 'go_to_real_geostranger_account')
