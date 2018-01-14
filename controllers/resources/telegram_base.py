# coding=utf-8
import importlib
import logging
import os
import pkgutil
import re
from functools import wraps

import time
from geopy.geocoders import Nominatim

import datetime
from mongoengine.queryset.visitor import Q

from controllers.resources.languages import get_lang
from models import UserModel, HandlerModel, ConversationModel
from telebot import types


hideBoard = types.ReplyKeyboardRemove()  # if sent as reply_markup, will hide the keyboard


def trans_message(lang, what, format_with=None):
	if format_with is None:
		format_with = {}

	return get_lang(lang or 'en', what, format_with) or ''


def send_to_user(telegram, chat_id, lang, what, handler=None, reply_markup=None, format_with=None, *args, **kwargs):
	if reply_markup is None:
		reply_markup = hideBoard

	msg = telegram.send_message(chat_id,
	                            trans_message(lang, what, format_with),
	                            parse_mode='markdown', reply_markup=reply_markup, *args, **kwargs)
	if handler:
		registry_handler(telegram, msg, handler)
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


def search_user_near(user):
	while True:
		selected_user = UserModel.objects(Q(id__ne=user.id) & \
		                                  Q(count_actual_conversation=0) & \
		                                  Q(location__near=user.location) & \
		                                  Q(location__min_distance=100) & \
		                                  Q(allow_search=True) & \
		                                  Q(completed=True)) \
			.modify(inc__count_actual_conversation=1, new=True)

		if not selected_user:
			return None

		if selected_user.count_actual_conversation == 1:
			return selected_user

		# nel caso sia stato già scelto
		selected_user.modify(inc__count_actual_conversation=-1)
		time.sleep(0.36)


def search_for_new_chat_near_user(telegram, message, actual_user):
	send_to_user(telegram, message.chat.id, message.from_user.language_code, 'in_search')

	user_found = search_user_near(actual_user)
	if not user_found:
		actual_user.allow_search = True
		actual_user.save()
		return

	conversation = ConversationModel(users=[actual_user, user_found])
	conversation.save()

	send_to_user(telegram, message.chat.id, message.from_user.language_code, 'found_new_geostranger_first_time',
	             format_with={'sex': trans_message(message.from_user.language_code,
	                                               'man') if user_found.sex == 'm' else trans_message(
		             message.from_user.language_code, 'female'), 'age': user_found.age}, handler='')


# WRAPPERS #

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


def user_exists_or_create(func):
	@wraps(func)
	def call(telegram, message, *args, **kwargs):
		user = UserModel.objects(chat_type=telegram.chat_type, user_id=str(message.from_user.id)).first()
		if not user:
			user = UserModel(chat_type=telegram.chat_type, user_id=str(message.from_user.id),
			                 language=message.from_user.language_code)

		return func(telegram, message, user, *args, **kwargs)

	return call


def user_exists(func):
	@wraps(func)
	def call(telegram, message, *args, **kwargs):
		user = UserModel.objects(chat_type=telegram.chat_type, user_id=str(message.from_user.id)).first()
		if not user:
			send_to_user(telegram, message.chat.id, message.from_user.language_code, 'user_required_but_not_found')

			command_start(telegram, message)
			return

		return func(telegram, message, user, *args, **kwargs)

	return call


# END WRAPPERS #

# HANDLERS #
@user_exists_or_create
def handler_position_step1(telegram, message, user):
	if message.location:
		user.location = [message.location.longitude, message.location.latitude]
		user.save()

		send_to_user(telegram, message.chat.id, message.from_user.language_code, 'ask_age', handler=handler_age_step)
		return

	if not message.text:
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


@user_exists
def handler_position_step2(telegram, message, user):
	if not check_response(message, 'yes'):
		""" Richiedo allora nuovamente la posizione """
		send_to_user(telegram, message.chat.id, message.from_user.language_code, 're_ask_location',
		             handler=handler_position_step1)
		return

	""" Location ok! """
	send_to_user(telegram, message.chat.id, message.from_user.language_code, 'ask_age', handler=handler_age_step)


@user_exists
def handler_age_step(telegram, message, user):
	age = re.findall('\\d+', message.text.strip())
	if not age or len(age) > 1:
		reply_to_message(telegram, message, 'age_error', handler=handler_age_step)

		return

	age = int(age[0])

	if age < 14:
		reply_to_message(telegram, message, 'age_error_to_low')

	user.age = age
	user.save()

	markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
	markup.add(trans_message(message.from_user.language_code, 'man'),
	           trans_message(message.from_user.language_code, 'female'))
	send_to_user(telegram, message.chat.id, message.from_user.language_code, 'ask_sex', reply_markup=markup,
	             handler=handler_sex_step)


@user_exists
def handler_exchange_message(telegram, message, user):
	x = types.InlineKeyboardButton()

	pass


@user_exists
def handler_sex_step(telegram, message, actual_user):
	sex = message
	if not check_response(message, 'man') and not check_response(message, 'female'):
		markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
		markup.add(trans_message(message.from_user.language_code, 'man'),
		           trans_message(message.from_user.language_code, 'female'))
		reply_to_message(telegram, message, 'sex_error', reply_markup=markup, handler=handler_sex_step)

		return

	actual_user.sex = 'm' if sex == trans_message(message.from_user.language_code, 'man') else 'f'
	actual_user.completed = True
	actual_user.save()
	send_to_user(telegram, message.chat.id, message.from_user.language_code, 'completed')

	search_for_new_chat_near_user(telegram, message, actual_user)


@user_exists
def handler_delete(telegram, message, user):
	if not check_response(message, 'yes'):
		send_to_user(telegram, message.chat.id, message.from_user.language_code, 'not_deleted')
		return

	user.deleted_at = datetime.datetime.utcnow()
	user.chat_id = None
	user.save()
	send_to_user(telegram, message.chat.id, message.from_user.language_code, 'delete_completed')


# END HANDLERS #

# COMMAND #

def command_terms(telegram, message, user=None):
	send_to_user(telegram, message.chat.id, message.from_user.language_code, 'terms')


def command_help(telegram, message, user=None):
	help_text = ''
	for key in telegram.commands:  # generate help text out of the commands dictionary defined at the top
		help_text += "/" + telegram.commands[key] + ": "
		help_text += trans_message(message.from_user.language_code, 'command_' + telegram.commands[key]) + "\n"

	send_to_user(telegram, message.chat.id, message.from_user.language_code, 'help',
	             format_with={'help_text': help_text})


def command_stop(telegram, message, user):
	user.allow_search = False
	user.save()

	send_to_user(telegram, message.chat.id, message.from_user.language_code, 'stop')


def command_delete_ask(telegram, message, user):
	markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
	markup.add(trans_message(message.from_user.language_code, 'yes'),
	           trans_message(message.from_user.language_code, 'no'))
	send_to_user(telegram, message.chat.id, message.from_user.language_code, 'delete_sure', reply_markup=markup,
	             handler=handler_delete)


def command_notify(telegram, message, user):
	send_to_user(telegram, message.chat.id, message.from_user.language_code, 'ask_notify', handler=handler_notify)


def handler_notify(telegram, message, user):
	message.text.encode('utf-8').strip()
	send_to_user(telegram, message.chat.id, message.from_user.language_code, 'notify_sent')


def command_start(telegram, message):
	actual_user = UserModel.objects(chat_type=telegram.chat_type, user_id=str(message.from_user.id),
	                                completed=True).first()
	if not actual_user:
		send_to_user(telegram, message.chat.id, message.from_user.language_code, 'start')
		send_to_user(telegram, message.chat.id, message.from_user.language_code, 'ask_location',
		             handler=handler_position_step1)

		return

	search_for_new_chat_near_user(telegram, message, actual_user)


def command_handler(telegram, message):
	""" Atomically get next handler """
	h = HandlerModel.objects(chat_type=telegram.chat_type, chat_id=str(message.chat.id)).modify(next_function='')
	if not h or not h.next_function:
		command_start(telegram, message)
		return

	try:
		globals()[h.next_function](telegram, message)
	except Exception as e:
		logging.exception(e)
		if h.next_function is not None:
			registry_handler(telegram, message, h.next_function)


# raise e


def registry_handler(telegram, message, handler_name):
	if not isinstance(handler_name, (str, unicode)):
		handler_name = handler_name.__name__

	HandlerModel.objects(chat_type=telegram.chat_type, chat_id=str(message.chat.id)) \
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
