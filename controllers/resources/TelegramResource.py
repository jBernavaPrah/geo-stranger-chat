# coding=utf-8

import geocoder
import telebot
from flask import request
from flask_restful import Resource
from telebot import types

import config
from models import User

telegram = telebot.TeleBot(config.TELEGRAM_KEY, threaded=False)

WEBHOOK = 'https://%s/v1/telegram/webhook/%s' % (config.SERVER_NAME, config.TELEGRAM_URL_KEY)

try:
	telegram.set_webhook(url=WEBHOOK)
except Exception as e:
	print e
	pass

commands = {  # command description used in the "help" command
	'start': 'Start as new user',
	'help': 'Gives you information about the available commands',

}

hideBoard = types.ReplyKeyboardRemove()  # if sent as reply_markup, will hide the keyboard

location_mark = types.ReplyKeyboardMarkup(one_time_keyboard=True,
										  resize_keyboard=True)  # create the image selection keyboard
location_button = types.KeyboardButton('Invia la posizione', request_location=True)
location_mark.row(location_button)


@telegram.message_handler(commands=['terms'])
def command_terms(message):
	telegram.send_message(message.chat.id,
						  'Thank you for shopping with our demo bot. We hope you like your new time machine!\n'
						  '1. If your time machine was not delivered on time, please rethink your concept of time and try again.\n'
						  '2. If you find that your time machine is not working, kindly contact our future service workshops on Trappist-1e.'
						  ' They will be accessible anywhere between May 2075 and November 4000 C.E.\n'
						  '3. If you would like a refund, kindly apply for one yesterday and we will have sent it to you immediately.')


# help page
@telegram.message_handler(commands=['help'])
def command_help(m):
	cid = m.chat.id
	help_text = "The following commands are available: \n"
	for key in commands:  # generate help text out of the commands dictionary defined at the top
		help_text += "/" + key + ": "
		help_text += commands[key] + "\n"
		telegram.send_message(cid, help_text)  # send the generated help page


@telegram.message_handler(commands=['start'])
def send_welcome(message):
	# elimino eventuali informazioni dell'utente, per non incorrere in errori.

	User(id=message.from_user.id).delete()

	user = User(id=message.from_user.id)
	user.name = message.from_user.first_name
	user.save()

	telegram.send_message(message.chat.id,
						  "Benvenuto {name}!\nTra poco inizierai a chattare con una persona.".format(
							  name=user.name))

	telegram.send_message(message.chat.id,
						  "Ti ricordo che la lista dei comandi la trovi su /help e continuando a chattare con il bot accetti i termini e le condizioni che trovi su /terms.")

	msg = telegram.send_message(message.chat.id,
								"Ma prima di iniziare devo farti la domanda più importante: dove ti trovi? (Clicca sul pulsante sotto)",
								reply_markup=location_mark)

	telegram.register_next_step_handler(msg, handler_position_step1)


def handler_position_step1(message):
	try:

		if message.location:
			user = User.get_by(id=message.from_user.id)
			user.location = message.location
			user.save_user()
			msg = telegram.send_message(message.chat.id, "Bene, Qual'è la tua età?")
			telegram.register_next_step_handler(msg, handler_age_step)
		else:
			msg = telegram.send_message(message.chat.id,
										"Non possiamo continuare se non mi invii la tua posizione (Non serve che sia esatta, puoi anche spostare il marker ;)",
										reply_markup=location_mark)
			telegram.register_next_step_handler(msg, handler_age_step)
	except Exception as e:
		telegram.reply_to(message, 'oooops')


def handler_name_step(message):
	try:
		chat_id = message.chat.id
		name = message.text
		user = User(name)
		user_dict[chat_id] = user
		msg = telegram.reply_to(message, 'How old are you?')
		telegram.register_next_step_handler(msg, handler_age_step)
	except Exception as e:
		telegram.reply_to(message, 'oooops')


def handler_age_step(message):
	try:
		chat_id = message.chat.id
		age = message.text
		if not age.isdigit():
			msg = telegram.reply_to(message, 'Age should be a number. How old are you?')
			telegram.register_next_step_handler(msg, handler_age_step)
			return
		user = user_dict[chat_id]
		user.age = age
		markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
		markup.add('Male', 'Female')
		msg = telegram.reply_to(message, 'What is your gender', reply_markup=markup)
		telegram.register_next_step_handler(msg, handler_sex_step)
	except Exception as e:
		telegram.reply_to(message, 'oooops')


def handler_sex_step(message):
	try:
		chat_id = message.chat.id
		sex = message.text
		user = user_dict[chat_id]
		if (sex == u'Male') or (sex == u'Female'):
			user.sex = sex
		else:
			raise Exception()
		telegram.send_message(chat_id,
							  'Nice to meet you ' + str(user.name) + '\n Age:' + str(user.age) + '\n Sex:' + user.sex)
	except Exception as e:
		telegram.reply_to(message, 'oooops')


class Telegram(Resource):
	def post(self):
		json_string = request.get_data().decode('utf-8')
		update = telebot.types.Update.de_json(json_string)
		telegram.process_new_updates([update])
		return ''
