# coding=utf-8
import datetime

import logging
import telebot
from flask import request
from flask_restful import Resource
from telebot import types
from functools import wraps

import config
from models import User, Handler
from mongoengine.queryset.visitor import Q

telegram = telebot.TeleBot(config.TELEGRAM_KEY, threaded=False)

WEBHOOK = 'https://%s/v1/telegram/webhook/%s' % (config.SERVER_NAME, config.TELEGRAM_URL_KEY)
CHAT_TYPE = 'telegram'

try:
	telegram.set_webhook(url=WEBHOOK)
except Exception as e:
	print e
	pass

commands = {  # command description used in the "help" command
	'start': 'Start',
	'delete': 'Delete your information from our database',
	'stop': 'Stop receiving new chats from strangers',
	'help': 'Gives you information about the available commands',

}

hideBoard = types.ReplyKeyboardRemove()  # if sent as reply_markup, will hide the keyboard

location_mark = types.ReplyKeyboardMarkup(one_time_keyboard=True,
										  resize_keyboard=True)  # create the image selection keyboard
location_button = types.KeyboardButton('Invia la posizione', request_location=True)
location_mark.row(location_button)


def registry_handler(message, handler):
	Handler.objects(chat_type=CHAT_TYPE, chat_id=str(message.chat.id)) \
		.modify(push__functions=handler.__name__, upsert=True)


def search_user_near(user):
	while True:
		user = User.objects(Q(id__ne=user.id) & \
							Q(count_actual_conversation=0) & \
							Q(location__near=user.location) & \
							Q(location__min_distance=100) & \
							Q(in_search=True) & \
							Q(completed=True)) \
			.modify(inc__count_actual_conversation=1, new=True)
		if not user:
			return None

		if user.count_actual_conversation == 1:
			return user

		release_user_near(user)


def release_user_near(user):
	user.modify(inc__count_actual_conversation=-1)


def wrap_exceptions(func):
	@wraps(func)
	def call(message, *args, **kwargs):
		try:
			return func(message, *args, **kwargs)
		except Exception as e:
			if message and hasattr(message, 'chat'):
				telegram.send_message(message.chat.id, "C'è stato un errore interno... :( Riprova..")

			logging.exception(e)

	return call


def user_exists(func):
	@wraps(func)
	def call(message, *args, **kwargs):
		user = User.objects(chat_type=CHAT_TYPE, chat_id=str(message.from_user.id)).first()
		if not user:
			telegram.send_message(message.chat.id, "Hmm... Non ti conosco.. Ma non importa :) Iniziamo! :) ")
			send_welcome(message)
			return

		return func(message, user, *args, **kwargs)

	return call


@telegram.message_handler(commands=['terms'])
@wrap_exceptions
def command_terms(message):
	telegram.send_message(message.chat.id,
						  'Thank you for shopping with our demo bot. We hope you like your new time machine!\n'
						  '1. If your time machine was not delivered on time, please rethink your concept of time and try again.\n'
						  '2. If you find that your time machine is not working, kindly contact our future service workshops on Trappist-1e.'
						  ' They will be accessible anywhere between May 2075 and November 4000 C.E.\n'
						  '3. If you would like a refund, kindly apply for one yesterday and we will have sent it to you immediately.')


# help page
@telegram.message_handler(commands=['help'])
@wrap_exceptions
def command_help(m):
	cid = m.chat.id
	help_text = "The following commands are available: \n"
	for key in commands:  # generate help text out of the commands dictionary defined at the top
		help_text += "/" + key + ": "
		help_text += commands[key] + "\n"
		telegram.send_message(cid, help_text)  # send the generated help page


@telegram.message_handler(commands=['stop'])
@wrap_exceptions
@user_exists
def command_help(message, user):
	user.in_search = False
	user.save()

	telegram.send_message(message.chat.id, "Ok stoppato. Se vuoi reiniziare, basta che clicchi su /start ;)")


@telegram.message_handler(commands=['delete'])
@wrap_exceptions
@user_exists
def command_help(message, user):
	markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
	markup.add('Sì', 'No')
	msg = telegram.send_message(message.chat.id, "Sei sicuro di voler cancellarti?", reply_markup=markup)

	registry_handler(msg, handler_delete)


@telegram.message_handler(commands=['start'])
@wrap_exceptions
def send_welcome(message):
	actual_user = User.objects(chat_type=CHAT_TYPE, chat_id=str(message.from_user.id)).first()
	if not actual_user:
		msg = telegram.send_message(message.chat.id,
									"Benvenuto \xF0\x9F\x98\x8B \xF0\x9F\x98\x8B!\n\nTra poco inizierai a chattare. \n\n Continuando con il bot accetti i termini e le condizioni che trovi su /terms.\n\nPotrai cancellarti in qualsiasi momento con il comando /delete. (La lista completa dei comandi la trovi su /help) \n\n Se sei d'accordo iniziaimo!\n\n\n Dove ti trovi? (Usa il tasto \xF0\x9F\x93\x8E -> \"Posizione\") ",
									reply_markup=hideBoard)

		registry_handler(msg, handler_position_step1)
		return

	actual_user.in_search = True
	actual_user.save()

	search_for_new_chat_near_user(message, actual_user)


@telegram.message_handler(func=lambda message: True,
						  content_types=['audio', 'video', 'document', 'text', 'location', 'contact', 'sticker'])
@wrap_exceptions
@user_exists
def exec_handlers(message, user):
	h = Handler.objects(chat_type=CHAT_TYPE, chat_id=str(message.chat.id)).first()
	if not h or not len(h.functions):
		send_welcome(message)

	fs = h.functions
	h.functions = []
	h.save()

	for f in fs:
		globals()[f](message, user)


@wrap_exceptions
def handler_position_step1(message, user):
	if message.location:
		user.location = [message.location.latitude, message.location.longitude]
		user.save()

		msg = telegram.send_message(message.chat.id, "Bene, qual'è la tua età?", reply_markup=hideBoard)
		registry_handler(msg, handler_age_step)

	else:
		msg = telegram.send_message(message.chat.id,
									"Non possiamo continuare se non mi invii la tua posizione. :( \n\n (Usa il tasto \xF0\x9F\x93\x8E -> \"Posizione\") \n\n La posizione non serve che sia esatta, puoi anche spostare il marker \xF0\x9F\x98\x84")
		registry_handler(msg, handler_position_step1)


@wrap_exceptions
def handler_age_step(message, user):
	age = message.text
	if not age.isdigit():
		msg = telegram.reply_to(message, 'Mandami solo il numero di anni :)')
		registry_handler(msg, handler_age_step)

		return

	user.age = age
	user.save()

	markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
	markup.add('Maschio', 'Femmina')
	msg = telegram.send_message(message.chat.id, 'Salvato :) Sei maschio o femmina?', reply_markup=markup)
	registry_handler(msg, handler_sex_step)


@wrap_exceptions
def handler_sex_step(message, actual_user):
	sex = message.text
	if (sex != 'Maschio') and (sex != 'Femmina'):
		markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
		markup.add('Maschio', 'Femmina')
		msg = telegram.reply_to(message, 'Seleziona se sei maschio o femmina..', reply_markup=markup)
		registry_handler(msg, handler_sex_step)
		return

	actual_user.sex = 'm' if sex == 'Maschio' else 'f'

	actual_user.save()

	completed_user_information(message, actual_user)
	search_for_new_chat_near_user(message, actual_user)


@wrap_exceptions
def completed_user_information(message, actual_user):
	telegram.send_message(message.chat.id, 'Bene! :) Abbiamo finito, ora iniziamo.. ', reply_markup=hideBoard)

	telegram.send_message(message.chat.id,
						  'Ora tutti i messaggi che invierai a me verranno spediti al utente anonimo con cui stai chattando.')

	telegram.send_message(message.chat.id, 'Ti ricordo di non comportarti male. ')


@wrap_exceptions
def search_for_new_chat_near_user(message, actual_user):
	telegram.send_message(message.chat.id, 'Inizio a cercare..')

	user_found = search_user_near(actual_user)
	if not user_found:
		actual_user.in_search = True
		actual_user.save()
		return


@wrap_exceptions
def handler_delete(message, user):
	resp = message.text
	if resp != 'Sì':
		telegram.send_message(message.chat.id, "Bene, non ho cancellato nulla. ", reply_markup=hideBoard)
		return

	user.deleted_at = datetime.datetime.utcnow()
	user.chat_id = None
	user.save()

	telegram.send_message(message.chat.id,
						  "Ok, ho cancellato i tuoi dati. Ti ricordo che devi eliminare anche tutta la cronologia sul tuo cellulare.\n\n Mi dispiace che te ne vai.\nQuando vorrai tornare, inizia semplicemente con il tasto /start o scrivimi qualcosa! :)",
						  reply_markup=hideBoard)


class Telegram(Resource):
	def post(self):
		json_string = request.get_data().decode('utf-8')
		update = telebot.types.Update.de_json(json_string)
		telegram.process_new_updates([update])
		return ''
