# coding=utf-8
import telebot
import config
from controllers.resources.telegram_base import message_handler

telegram_online = telebot.TeleBot(config.TELEGRAM_KEY, threaded=False)
telegram_online.chat_type = 'telegram'
telegram_online.commands = ['start',
							'stop',
							'delete',
							'terms',
							'notify',
							'help', ]  # command description used in the "help" command

message_handler(telegram_online)
