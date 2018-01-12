# coding=utf-8
import telebot
import config
from controllers.resources.telegram_base import message_handler

geostranger = telebot.TeleBot(config.GEOSTRANGER_KEY, threaded=False)
geostranger.chat_type = 'telegram'
geostranger.commands = ['start',
						'stop',
						'delete',
						'terms',
						'notify',
						'help', ]  # command description used in the "help" command

message_handler(geostranger)
