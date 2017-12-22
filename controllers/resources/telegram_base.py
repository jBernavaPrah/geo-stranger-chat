# coding=utf-8
import importlib
import logging
import os
import pkgutil
import re
from functools import wraps
from geopy.geocoders import Nominatim

import datetime
from mongoengine.queryset.visitor import Q

from controllers.resources.languages import get_lang
from models import User, Handler
from telebot import types

hideBoard = types.ReplyKeyboardRemove()  # if sent as reply_markup, will hide the keyboard


def trans_message(message, what, **kwargs):
	return get_lang(message.from_user.language_code or 'en', what, **kwargs) or ''


def send_to_user(telegram, message, what, reply_markup=None, *args, **kwargs):
	if reply_markup is None:
		reply_markup = hideBoard
	return telegram.send_message(message.chat.id,
	                             trans_message(message, what, **kwargs),
	                             parse_mode='markdown', reply_markup=reply_markup, *args, **kwargs)



def reply_to_message(telegram, message, what, *args, **kwargs):
	return telegram.reply_to(message, trans_message(message, what),
	                         parse_mode='markdown', *args, **kwargs)


def search_user_near(user):
	while True:
		user = User.objects(Q(id__ne=user.id) & \
		                    Q(count_actual_conversation=0) & \
		                    Q(location__near=user.location) & \
		                    Q(location__min_distance=100) & \
		                    Q(allow_search=True) & \
		                    Q(completed=True)) \
			.modify(inc__count_actual_conversation=1, new=True)

		if not user:
			return None

		if user.count_actual_conversation == 1:
			return user

		release_user_near(user)


def release_user_near(user):
	user.modify(inc__count_actual_conversation=-1)


def search_for_new_chat_near_user(telegram, message, actual_user):
	send_to_user(telegram, message, 'in_search')

	user_found = search_user_near(actual_user)
	if not user_found:
		actual_user.allow_search = True
		actual_user.save()
		return

	send_to_user(telegram, message, 'found_new_geostranger_first_time',
	             sex=trans_message(message, 'man') if user_found.sex == 'm' else trans_message(
		             message, 'female'),
	             age=user_found.age)


# WRAPPERS #

def wrap_exceptions(func):
	@wraps(func)
	def call(telegram, message, *args, **kwargs):
		try:
			return func(telegram, message, *args, **kwargs)
		except Exception as e:
			if message and hasattr(message, 'chat'):
				send_to_user(telegram, message, 'error')

			logging.exception(e)

	return call


def wrap_telegram(telegram):
	def wt(func):
		@wraps(func)
		def call(message, *args, **kwargs):
			return func(telegram, message, *args, **kwargs)

		return call

	return wt


def user_exists_or_create(func):
	@wraps(func)
	def call(telegram, message, *args, **kwargs):
		user = User.objects(chat_type=telegram.chat_type, user_id=str(message.from_user.id)).first()
		if not user:
			user = User(chat_type=telegram.chat_type, user_id=str(message.from_user.id),
			            language=message.from_user.language_code)

		return func(telegram, message, user, *args, **kwargs)

	return call


def user_exists(func):
	@wraps(func)
	def call(telegram, message, *args, **kwargs):
		user = User.objects(chat_type=telegram.chat_type, user_id=str(message.from_user.id)).first()
		if not user:
			send_to_user(telegram, message, 'user_required_but_not_found')

			command_start(telegram, message)
			return

		return func(telegram, message, user, *args, **kwargs)

	return call


# END WRAPPERS #

# HANDLERS #
@user_exists_or_create
def handler_position_step1(telegram, message, user):
	if message.location:
		user.location = [message.location.latitude, message.location.longitude]
		user.save()

		msg = send_to_user(telegram, message, 'ask_age')
		registry_handler(telegram, msg, handler_age_step)
		return

	if not message.text:
		msg = send_to_user(telegram, message, 'location_error')
		registry_handler(telegram, msg, handler_position_step1)

	geolocator = Nominatim()
	location = geolocator.geocode(message.text.encode('utf8').strip(), language=message.from_user.language_code)

	if not location:
		""" Location non trovata.. """
		msg = send_to_user(telegram, message, 'location_not_found')
		registry_handler(telegram, msg, handler_position_step1)
		return

	""" Location trovata! Per il momento la salvo e chiedo se è corretta :) """
	user.location = [location.latitude, location.longitude]
	user.save()

	markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
	markup.add(trans_message(message, 'yes'), trans_message(message, 'no'))
	msg = send_to_user(telegram, message, 'location_is_correct_message', location_text=location.address,
	                   reply_markup=markup)

	registry_handler(telegram, msg, handler_position_step2)


@user_exists
def handler_position_step2(telegram, message, user):
	if message.text.encode('utf-8').strip() != telegram.yes_message:
		""" Richiedo allora nuovamente la posizione """
		msg = send_to_user(telegram, message, 're_ask_location')
		registry_handler(telegram, msg, handler_position_step1)
		return

	""" Location ok! """
	msg = send_to_user(telegram, message, 'ask_age')
	registry_handler(telegram, msg, handler_age_step)


@user_exists
def handler_age_step(telegram, message, user):
	age = re.findall('\\d+', message.text.encode('utf8').strip())
	if not age or len(age) > 1:
		msg = reply_to_message(telegram, message, 'age_error')
		registry_handler(telegram, msg, handler_age_step)
		return

	age = int(age[0])

	if age < 14:
		reply_to_message(telegram, message, 'age_error_to_low')

	if age > 85:
		reply_to_message(telegram, message, 'age_error_to_high', age=age)

	user.age = age
	user.save()

	markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
	markup.add(telegram.man_message, telegram.female_message)
	msg = send_to_user(telegram, message, 'ask_sex', reply_markup=markup)

	registry_handler(telegram, msg, handler_sex_step)


@user_exists
def handler_sex_step(telegram, message, actual_user):
	sex = message.text.encode('utf8').strip()
	if (sex != telegram.man_message) and (sex != telegram.female_message):
		markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
		markup.add(trans_message(message, 'man'), trans_message(message, 'female'))
		msg = reply_to_message(telegram, message, 'sex_error', reply_markup=markup)
		registry_handler(telegram, msg, handler_sex_step)
		return

	actual_user.sex = 'm' if sex == trans_message(message, 'man') else 'f'
	actual_user.completed = True
	actual_user.save()
	send_to_user(telegram, message, 'completed')

	search_for_new_chat_near_user(telegram, message, actual_user)


@user_exists
def handler_delete(telegram, message, user):
	if message.text.encode('utf-8').strip() != trans_message(message, 'yes'):
		send_to_user(telegram, message, 'not_deleted')
		return

	user.deleted_at = datetime.datetime.utcnow()
	user.chat_id = None
	user.save()
	send_to_user(telegram, message, 'delete_completed')


# END HANDLERS #

# COMMAND #

def command_terms(telegram, message, user=None):
	send_to_user(telegram, message.chat.id, telegram.terms)


def command_help(telegram, message, user=None):
	help_text = ''
	for key in telegram.commands:  # generate help text out of the commands dictionary defined at the top
		help_text += "/" + telegram.commands[key] + ": "
		help_text += trans_message(message, 'command_' + telegram.commands[key]) + "\n"

	send_to_user(telegram, message, 'help', help_text=help_text)


def command_stop(telegram, message, user):
	user.allow_search = False
	user.save()

	send_to_user(telegram, message, 'stop')


def command_delete_ask(telegram, message, user):
	markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
	markup.add(trans_message(message, 'yes'), trans_message(message, 'no'))
	msg = send_to_user(telegram, message, 'delete_sure', reply_markup=markup)

	registry_handler(telegram, msg, handler_delete)

def command_notify(telegram,message,user):
	msg = send_to_user(telegram, message, 'ask_notify')

	registry_handler(telegram, msg, handler_notify)


def handler_notify(telegram, message, user):
	message.text.encode('utf-8').strip()
	send_to_user(telegram, message, 'notify_sent')

def command_start(telegram, message):
	actual_user = User.objects(chat_type=telegram.chat_type, user_id=str(message.from_user.id), completed=True).first()
	if not actual_user:
		markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
		markup.add(trans_message(message, 'yes'), trans_message(message, 'no'))
		msg = send_to_user(telegram, message, 'start')

		registry_handler(telegram, msg, handler_terms_accept)
		return

	search_for_new_chat_near_user(telegram, message, actual_user)

def handler_terms_accept(telegram,message):
	if message.text.encode('utf-8').strip() != telegram.yes_message:
		""" Utente non ha accettato le condizioni :( """
		send_to_user(telegram, message, 'byebye')
		return

	msg = send_to_user(telegram, message, 'ask_location')

	registry_handler(telegram, msg, handler_position_step1)
	return


def command_handler(telegram, message):
	""" Atomically get next handler """
	h = Handler.objects(chat_type=telegram.chat_type, chat_id=str(message.chat.id)).modify(next_function='')
	if not h or not h.next_function:
		command_start(telegram, message)

	try:
		globals()[h.next_function](telegram, message)
	except Exception as e:
		logging.exception(e)
		registry_handler(telegram, message, h.next_function)
		raise e


def registry_handler(telegram, message, handler_name):
	if not isinstance(handler_name, (str, unicode)):
		handler_name = handler_name.__name__

	Handler.objects(chat_type=telegram.chat_type, chat_id=str(message.chat.id)) \
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

	@telegram.message_handler(commands=['stop'])
	@wrap_telegram(telegram)
	@wrap_exceptions
	@user_exists
	def execute(*args, **kwargs):
		command_stop(*args, **kwargs)

	@telegram.message_handler(commands=['delete'])
	@wrap_telegram(telegram)
	@wrap_exceptions
	@user_exists
	def execute(*args, **kwargs):
		command_delete_ask(*args, **kwargs)

	@telegram.message_handler(commands=['notify'])
	@wrap_telegram(telegram)
	@wrap_exceptions
	@user_exists
	def execute(*args, **kwargs):
		command_notify(*args, **kwargs)

	@telegram.message_handler(commands=['start'])
	@wrap_telegram(telegram)
	@wrap_exceptions
	def execute(*args, **kwargs):
		command_start(*args, **kwargs)

	@telegram.message_handler(func=lambda message: True,
	                          content_types=['audio', 'video', 'document', 'text', 'location', 'contact', 'sticker'])
	@wrap_telegram(telegram)
	@wrap_exceptions
	def execute(*args, **kwargs):
		command_handler(*args, **kwargs)
