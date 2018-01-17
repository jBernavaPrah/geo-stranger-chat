# coding=utf-8
import logging
from functools import wraps

from geopy.geocoders import Nominatim

import datetime
from mongoengine.queryset.visitor import Q

from controllers.resources.languages import get_lang
from models import UserModel, MessageModel
from telebot import types

hideBoard = types.ReplyKeyboardRemove()  # if sent as reply_markup, will hide the keyboard


# WRAPPERS #


def wrap_user_exists(strict=True):
	# todo: Add other variable to specific what do if not found user.
	def x(func):
		@wraps(func)
		def call(telegram, message, user=None, *args, **kwargs):

			# In questa maniera posso gestire anche il richiamo diretto da funzione interna.
			if not isinstance(user, UserModel):
				user = UserModel.objects(chat_type=telegram.chat_type, user_id=str(message.from_user.id)).first()

			if not user and strict:
				logging.exception('User required, but not found.')
				raise

			return func(telegram, message, user, *args, **kwargs)

		return call

	return x


def wrap_exceptions(func):
	@wraps(func)
	def call(telegram, message, *args, **kwargs):
		try:
			return func(telegram, message, *args, **kwargs)
		except Exception as e:
			if message and hasattr(message, 'chat'):
				send_to_user(telegram, message.chat.id, message.from_user.language_code, 'error')

			logging.exception(e)

	return call


def wrap_telegram(telegram):
	def wt(func):
		@wraps(func)
		def call(message, *args, **kwargs):
			return func(telegram, message, *args, **kwargs)

		return call

	return wt


# END WRAPPERS #

# FUNCTIONS #

def trans_message(lang, what, format_with=None):
	if format_with is None:
		format_with = {}

	return get_lang(lang or 'en', what, format_with) or what


def send_to_user(telegram, user_id, lang, what, handler=None, reply_markup=None, format_with=None, *args, **kwargs):
	if reply_markup is None:
		reply_markup = hideBoard

	msg = telegram.send_message(user_id,
								trans_message(lang, what, format_with),
								parse_mode='markdown', reply_markup=reply_markup, *args, **kwargs)

	"""Registry handler"""
	registry_handler(telegram, user_id, handler)

	return msg


def reply_to_message(telegram, message, what, format_with=None, *args, **kwargs):
	return telegram.reply_to(message, trans_message(message.from_user.language_code, what, format_with),
							 parse_mode='markdown', *args, **kwargs)


def check_response(message, what, strict=False):
	m = message.text
	w = trans_message(message.from_user.language_code, what)

	if not strict:
		return m.lower().strip() == w.lower().strip()

	return m == w


# END FUNCTIONS #

# HANDLERS #

def handler_position_step1(telegram, message, user):
	if message.location:
		user.location = [message.location.longitude, message.location.latitude]
		user.save()

		user.completed = True
		user.save()
		send_to_user(telegram, message.chat.id, message.from_user.language_code, 'completed')

		return

	if not message.text.encode('utf8').strip():
		send_to_user(telegram, message.chat.id, message.from_user.language_code, 'location_error',
					 handler=handler_position_step1)
	location_text = message.text.encode('utf8').strip()
	geolocator = Nominatim()
	location = geolocator.geocode(location_text, language=message.from_user.language_code)

	if not location:
		""" Location non trovata.. """
		send_to_user(telegram, message.chat.id, message.from_user.language_code, 'location_not_found',
					 handler=handler_position_step1,
					 format_with={'location_text': location_text})
		return

	""" Location trovata! Per il momento la salvo e chiedo se è corretta :) """
	user.location = [location.longitude, location.latitude]
	user.save()

	markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
	markup.add(trans_message(message.from_user.language_code, 'yes'),
			   trans_message(message.from_user.language_code, 'no'))
	send_to_user(telegram, message.chat.id, message.from_user.language_code, 'location_is_correct',
				 reply_markup=markup, handler=handler_position_step2, format_with={'location_text': location.address})


def handler_position_step2(telegram, message, user):
	if not check_response(message, 'yes'):
		""" Richiedo allora nuovamente la posizione """
		send_to_user(telegram, message.chat.id, message.from_user.language_code, 're_ask_location',
					 handler=handler_position_step1)
		return

	""" Location ok! """
	# send_to_user(telegram, message.chat.id, message.from_user.language_code, 'ask_age', handler=handler_age_step)
	user.completed = True
	user.save()
	send_to_user(telegram, message.chat.id, message.from_user.language_code, 'completed')


# @user_exists
# def handler_age_step(telegram, message, user):
# 	age = re.findall('\\d+', message.text.strip())
# 	if not age or len(age) > 1:
# 		reply_to_message(telegram, message, 'age_error', handler=handler_age_step)
#
# 		return
#
# 	age = int(age[0])
#
# 	if age < 14:
# 		reply_to_message(telegram, message, 'age_error_to_low')
#
# 	user.age = age
# 	user.save()
#
# 	markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
# 	markup.add(trans_message(message.from_user.language_code, 'man'),
# 			   trans_message(message.from_user.language_code, 'female'))
# 	send_to_user(telegram, message.chat.id, message.from_user.language_code, 'ask_sex', reply_markup=markup,
# 				 handler=handler_sex_step)
#
#
# @user_exists
# def handler_sex_step(telegram, message, actual_user):
# 	sex = message
# 	if not check_response(message, 'man') and not check_response(message, 'female'):
# 		markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
# 		markup.add(trans_message(message.from_user.language_code, 'man'),
# 				   trans_message(message.from_user.language_code, 'female'))
# 		reply_to_message(telegram, message, 'sex_error', reply_markup=markup, handler=handler_sex_step)
#
# 		return
#
# 	actual_user.sex = 'm' if sex == trans_message(message.from_user.language_code, 'man') else 'f'
# 	actual_user.completed = True
# 	actual_user.save()
# 	send_to_user(telegram, message.chat.id, message.from_user.language_code, 'completed')
#
# 	_search_for_new_chat_near_user(telegram, message, actual_user)


def handler_delete(telegram, message, user):
	if not check_response(message, 'yes'):
		send_to_user(telegram, message.chat.id, message.from_user.language_code, 'not_deleted')
		return

	user.deleted_at = datetime.datetime.utcnow()
	user.user_id = None
	user.save()
	send_to_user(telegram, message.chat.id, message.from_user.language_code, 'delete_completed')


def handler_notify(telegram, message):
	message.text.encode('utf-8').strip()
	send_to_user(telegram, message.chat.id, message.from_user.language_code, 'notify_sent')


# END HANDLERS #


# COMMAND #


def command_terms(telegram, message):
	send_to_user(telegram, message.chat.id, message.from_user.language_code, 'terms')


def command_help(telegram, message):
	help_text = ''
	for key in telegram.commands:  # generate help text out of the commands dictionary defined at the top
		help_text += "/" + telegram.commands[key] + ": "
		help_text += trans_message(message.from_user.language_code, 'command_' + telegram.commands[key]) + "\n"

	send_to_user(telegram, message.chat.id, message.from_user.language_code, 'help',
				 format_with={'help_text': help_text})


@wrap_user_exists()
def command_search(telegram, message, actual_user):
	# TODO: controlla se l'utente non è in coversazione, altrimenti esegui il command_stop.

	if not actual_user.allow_search:
		actual_user.allow_search = True
		actual_user.save()

	msg = send_to_user(telegram, message.chat.id, message.from_user.language_code, 'in_search')

	# L'utente fa il search. Posso utilizzarlo solamente se l'utente non è al momento sotto altra conversation.
	# Questo vuol dire che non devo fare nessun ciclo. E' UNA FUNZIONE ONE SHOT!
	# E se non trovo nulla, devo aspettare che sia un altro a fare questa operazione e "Trovarmi"..
	#

	user_found = UserModel.objects(Q(id__ne=actual_user.id) & \
								   Q(chat_with=None) & \
								   Q(allow_search=True) & \
								   Q(completed=True) & \
								   Q(location__near=actual_user.location)) \
		.modify(chat_with=actual_user, new=True)

	# Q(location__min_distance=100))
	""" Se non ho trovato nessuno, devo solo aspettare che il sistema mi associ ad un altro geostranger. """
	if not user_found:
		""" Se non ho trovato nulla e non sono stato selezionato, aspetto.. succederà prima o poi :) """
		return

	"""Effettuo il reload per caricare l'ultima versione del modello"""
	actual_user.reload()
	if actual_user.chat_with:
		""" Se sono già stato scelto durante questa query, allora semplicemente effettuo il release del utente.  """

		user_found.chat_with = None
		user_found.save()
		return

	""" Eliminio il messaggio """
	telegram.delete_message(msg.chat.id, msg.message_id)

	actual_user.chat_with = user_found
	actual_user.save()

	if actual_user.first_time_chat:
		send_to_user(telegram, message.chat.id, message.from_user.language_code, 'found_new_geostranger_first_time')
		actual_user.first_time_chat = False
		actual_user.save()
	else:
		send_to_user(telegram, message.chat.id, message.from_user.language_code, 'found_new_geostranger')

	"""Invia il messaggio al utente selezionato """

	if user_found.first_time_chat:
		send_to_user(telegram, user_found.user_id, user_found.language, 'found_new_geostranger_first_time')
		user_found.first_time_chat = False
		user_found.save()
	else:
		send_to_user(telegram, user_found.user_id, user_found.language, 'found_new_geostranger')


@wrap_user_exists()
def command_stop(telegram, message, user):
	# TODO: Are you sure to stop messaging?
	# This will also stop receiving new geostrangers. To reactive send /search.

	if user.chat_with:
		send_to_user(telegram, user.chat_with.user_id, user.chat_with.language,
					 'conversation_stopped_by_other_geostranger')

		user.chat_with.chat_with = None
		user.chat_with.save()

	user.chat_with = None
	user.allow_search = False
	user.save()

	send_to_user(telegram, message.chat.id, message.from_user.language_code, 'stop')


@wrap_user_exists()
def command_delete(telegram, message, user):
	markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
	markup.add(trans_message(message.from_user.language_code, 'yes'),
			   trans_message(message.from_user.language_code, 'no'))
	send_to_user(telegram, message.chat.id, message.from_user.language_code, 'delete_sure', reply_markup=markup,
				 handler=handler_delete)


def command_notify(telegram, message):
	send_to_user(telegram, message.chat.id, message.from_user.language_code, 'ask_notify', handler=handler_notify)


@wrap_user_exists(False)
def command_start(telegram, message, user):
	if not user:
		user = UserModel(chat_type=telegram.chat_type, user_id=str(message.from_user.id),
						 language=message.from_user.language_code)
		user.save()
		send_to_user(telegram, message.chat.id, message.from_user.language_code, 'start')

	if not user.location:
		command_location(telegram, message, user)
		return

	"""User is completed, need a seach or change the location?"""


@wrap_user_exists()
def command_location(telegram, message, user):
	""" Se la location è già presente... La tua locazione al momento é: Vuoi cambiarla? Si no (inline button)"""

	send_to_user(telegram, message.chat.id, message.from_user.language_code, 'ask_location',
				 handler=handler_position_step1)


@wrap_user_exists(False)
def command_handler(telegram, message, user):
	if not user or (not user.chat_with and not user.next_function):
		command_start(telegram, message, user)
		return

	if user.next_function:
		try:
			return globals()[user.next_function](telegram, message, user)
		except Exception as e:
			logging.exception(e)
			registry_handler(telegram, message, user.next_function)
			return

	m = MessageModel(user=user)
	m.from_message(message)
	m.save()

	if not user.chat_with:
		send_to_user(telegram, message.chat.id, message.from_user.language_code,
					 'conversation_stopped_by_other_geostranger')
		return

	telegram.send_message(user.chat_with.user_id, '*GeoStranger:* ' + message.text,
						  parse_mode='markdown')


# raise e


def registry_handler(telegram, user_id, handler_name):
	if handler_name and hasattr(handler_name, '__name__'):
		handler_name = handler_name.__name__

	UserModel.objects(chat_type=telegram.chat_type, user_id=str(user_id)) \
		.modify(next_function=handler_name, upsert=True)


# END COMMAND #


def message_handler(telegram):
	@telegram.message_handler(commands=['terms'])
	@wrap_telegram(telegram)
	@wrap_exceptions
	def execute(*args, **kwargs):
		command_terms(*args, **kwargs)

	# help page
	@telegram.message_handler(commands=['help'])
	@wrap_telegram(telegram)
	@wrap_exceptions
	def execute(*args, **kwargs):
		command_help(*args, **kwargs)

	@telegram.message_handler(commands=['delete'])
	@wrap_telegram(telegram)
	@wrap_exceptions
	@wrap_user_exists
	def execute(*args, **kwargs):
		command_delete(*args, **kwargs)

	@telegram.message_handler(commands=['notify'])
	@wrap_telegram(telegram)
	@wrap_exceptions
	@wrap_user_exists
	def execute(*args, **kwargs):
		command_notify(*args, **kwargs)

	@telegram.message_handler(commands=['search'])
	@wrap_telegram(telegram)
	@wrap_exceptions
	def execute(*args, **kwargs):
		command_search(*args, **kwargs)

	@telegram.message_handler(commands=['stop'])
	@wrap_telegram(telegram)
	@wrap_exceptions
	def execute(*args, **kwargs):
		command_stop(*args, **kwargs)

	@telegram.message_handler(commands=['start'])
	@wrap_telegram(telegram)
	@wrap_exceptions
	def execute(*args, **kwargs):
		command_start(*args, **kwargs)

	@telegram.message_handler(func=lambda *_: True)
	@wrap_telegram(telegram)
	@wrap_exceptions
	def execute(*args, **kwargs):
		command_handler(*args, **kwargs)
