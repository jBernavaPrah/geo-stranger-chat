# coding=utf-8
import logging
from functools import wraps
from geopy.geocoders import Nominatim

import datetime
from mongoengine.queryset.visitor import Q
from models import User, Handler
from telebot import types

hideBoard = types.ReplyKeyboardRemove()  # if sent as reply_markup, will hide the keyboard



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


# WRAPPERS #

def wrap_exceptions(func):
	@wraps(func)
	def call(telegram, message, *args, **kwargs):
		try:
			return func(telegram, message, *args, **kwargs)
		except Exception as e:
			if message and hasattr(message, 'chat'):
				telegram.send_message(message.chat.id, telegram.error_message)

			logging.exception(e)

	return call


def wrap_telegram(telegram):
	def wt(func):
		@wraps(func)
		def call(message, *args, **kwargs):
			return func(telegram, message, *args, **kwargs)

		return call

	return wt


def user_exists(func):
	@wraps(func)
	def call(telegram, message, *args, **kwargs):
		user = User.objects(chat_type=telegram.chat_type, user_id=str(message.from_user.id)).first()
		if not user:
			telegram.send_message(message.chat.id, telegram.user_required_but_not_found)
			command_start(telegram, message)
			return

		return func(message, user, *args, **kwargs)

	return call


# END WRAPPERS #

# HANDLERS #

@wrap_exceptions
def handler_position_step1(telegram, message, user):
	if message.location:
		user.location = [message.location.latitude, message.location.longitude]
		user.save()

		msg = telegram.send_message(message.chat.id, telegram.age_ask_message)
		registry_handler(telegram, msg, handler_age_step)
		return

	if not message.text:
		msg = telegram.send_message(message.chat.id, telegram.location_error_message)
		registry_handler(telegram, msg, handler_position_step1)

	geolocator = Nominatim()
	location = geolocator.geocode(message.text, language=message.from_user.language)

	if not location:
		""" Location non trovata.. """
		msg = telegram.send_message(message.chat.id, telegram.location_not_found_message)
		registry_handler(telegram, msg, handler_position_step1)
		return

	""" Location trovata! :) """
	user.location = [location.latitude, location.longitude]
	user.save()

	msg = telegram.send_message(message.chat.id,
								telegram.location_is_correct_message.format(location_text=location.address))
	registry_handler(telegram, msg, handler_age_step)


@wrap_exceptions
def handler_position_step2(telegram, message, user):
	if message.text is not telegram.yes_message:
		""" Richiedo allora nuovamente la posizione """
		msg = telegram.send_message(message.chat.id, telegram.location_ask_message, reply_markup=hideBoard)
		registry_handler(telegram, msg, handler_position_step1)
		return

	""" Location ok! """
	msg = telegram.send_message(message.chat.id, telegram.age_ask_message)
	registry_handler(telegram, msg, handler_age_step)


@wrap_exceptions
def handler_age_step(telegram, message, user):
	age = message.text
	if not age.isdigit():
		msg = telegram.reply_to(message, telegram.age_error_message)
		registry_handler(telegram, msg, handler_age_step)
		return

	user.age = age
	user.save()

	markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
	markup.add(telegram.man_message, telegram.female_message)
	msg = telegram.send_message(message.chat.id, telegram.sex_ask_message, reply_markup=markup)
	registry_handler(telegram, msg, handler_sex_step)


@wrap_exceptions
def handler_sex_step(telegram, message, actual_user):
	sex = message.text
	if (sex != telegram.man_message) and (sex != telegram.female_message):
		markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
		markup.add(telegram.man_message, telegram.female_message)
		msg = telegram.reply_to(message, telegram.sex_error_message, reply_markup=markup)
		registry_handler(telegram, msg, handler_sex_step)
		return

	actual_user.sex = 'm' if sex == telegram.man_message else 'f'

	actual_user.save()

	telegram.send_message(message.chat.id, telegram.completed_message, reply_markup=hideBoard)

	search_for_new_chat_near_user(telegram, message, actual_user)


@wrap_exceptions
def search_for_new_chat_near_user(telegram, message, actual_user):
	telegram.send_message(message.chat.id, telegram.in_search_message)

	user_found = search_user_near(actual_user)
	if not user_found:
		actual_user.in_search = True
		actual_user.save()
		return

	telegram.send_message(message.chat.id,
						  telegram.found_new_geostranger_message.format(
							  sex=telegram.man_message if user_found.sex == 'm' else telegram.female_message,
							  age=user_found.age

						  ))


@wrap_exceptions
def handler_delete(telegram, message, user):
	resp = message.text
	if resp != telegram.yes_message:
		telegram.send_message(message.chat.id, telegram.not_deleted_message, reply_markup=hideBoard)
		return

	user.deleted_at = datetime.datetime.utcnow()
	user.chat_id = None
	user.save()

	telegram.send_message(message.chat.id,
						  telegram.delete_completed_message,
						  reply_markup=hideBoard)


# END HANDLERS #

# COMMAND #

def command_terms(telegram, message, user=None):
	telegram.send_message(message.chat.id, telegram.terms)


def command_help(telegram, message, user=None):
	help_text = '*' + telegram.help_message + '*\n\n'
	for key in telegram.commands:  # generate help text out of the commands dictionary defined at the top
		help_text += "/" + key + ": "
		help_text += telegram.commands[key] + "\n"


	telegram.send_message(message.chat.id, help_text, parse_mode='markdown')  # send the generated help page


def command_stop(telegram, message, user):
	user.in_search = False
	user.save()

	telegram.send_message(message.chat.id, telegram.stop_message)


def command_delete_ask(telegram, message, user):
	markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
	markup.add(telegram.yes_message, telegram.no_message)
	msg = telegram.send_message(message.chat.id, telegram.delete_sure_message, reply_markup=markup)

	registry_handler(telegram, msg, handler_delete)


def command_start(telegram, message):
	actual_user = User.objects(chat_type=telegram.chat_type, user_id=str(message.from_user.id)).first()
	if not actual_user:
		telegram.send_message(message.chat.id, telegram.start_message, reply_markup=hideBoard)
		msg = telegram.send_message(message.chat.id, telegram.location_ask_message, reply_markup=hideBoard)

		registry_handler(telegram, msg, handler_position_step1)
		return

	actual_user.in_search = True
	actual_user.save()

	search_for_new_chat_near_user(telegram, message, actual_user)


def command_handler(telegram, message, user):
	""" Atomically get next handler """
	h = Handler.objects(chat_type=telegram.chat_type, chat_id=str(message.chat.id)).modify(next_function='')
	if not h or not h.next_function:
		command_start(telegram, message)

	try:
		globals()[h.next_function](telegram, message, user)
	except Exception as e:
		logging.exception(e)
		registry_handler(telegram, message, h.next_function)
		raise e


def registry_handler(telegram, message, handler_name):
	if not isinstance(handler_name, str):
		handler_name = handler_name.__name__

	Handler.objects(chat_type=telegram.chat_type, chat_id=str(message.chat.id)) \
		.modify(next_function=handler_name, upsert=True)

# END COMMAND #
