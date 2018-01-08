# coding=utf-8
import telebot
import config
from controllers.resources.telegram_base import message_handler

telegram_test = telebot.TeleBot(config.TELEGRAM_TEST_KEY, threaded=False)
telegram_test.chat_type = 'telegram'
telegram_test.commands =['start',
							'stop',
							'delete',
							'terms',
							'notify',
							'help', ]

message_handler(telegram_test)
