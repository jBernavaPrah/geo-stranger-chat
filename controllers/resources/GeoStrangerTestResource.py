# coding=utf-8
import telebot
import config
from controllers.resources.telegram_base import message_handler

geostranger_test = telebot.TeleBot(config.GEOSTRANGER_TEST_KEY, threaded=False)
geostranger_test.chat_type = 'telegram'
geostranger_test.commands =['start',
							'stop',
							'delete',
							'terms',
							'notify',
							'help', ]

message_handler(geostranger_test)
