# coding=utf-8
import telebot
import config
from controllers.resources.telegram_base import message_handler

telegram_test = telebot.TeleBot(config.TELEGRAM_TEST_KEY, threaded=False)
telegram_test.chat_type = 'telegram'
telegram_test.commands = {  # command description used in the "help" command
	'start': 'Inizia una conversazione con un nuovo GeoStrangers',
	'stop': 'Smetto di inviarti nuovi GeoStrangers',
	'delete': 'Elimina i tuoi dati dalla piattaforma GeoStranger',
	'terms': 'I termini di utilizzo del contratto',
	'notify': "C'è qualcosa che vuoi farmi notare? Qualche bug? Provvederò a innoltrarlo alle scimmie che mi hanno creato.",
	'help': 'Lista di tutti i comandi.',
}

message_handler(telegram_test)
