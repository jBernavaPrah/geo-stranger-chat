# coding=utf-8
import logging
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
										  Q(chat_with__exists=True) & \
										  Q(location__near=user.location) & \
										  Q(location__min_distance=100) & \
										  Q(completed=True)) \
			.modify(inc__count_actual_conversation=1, new=True)

		if not selected_user:
			return None

		if selected_user.count_actual_conversation == 1:
			return selected_user

		# nel caso sia stato già scelto
		selected_user.modify(inc__count_actual_conversation=-1)
		time.sleep(0.36)


# WRAPPERS #

def wrap_user_exists(strict=True):
	# todo: Add other variable to specific what do if not found user.
	def x(func):
		@wraps(func)
		def call(telegram, message, *args, **kwargs):
			user = UserModel.objects(chat_type=telegram.chat_type, user_id=str(message.from_user.id)).first()
			if not user and strict:
				send_to_user(telegram, message.chat.id, message.from_user.language_code, 'user_required_but_not_found')

				command_start(telegram, message)
				return

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


@wrap_user_exists
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


# END WRAPPERS #


# HANDLERS #
@wrap_user_exists
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


@wrap_user_exists
def handler_delete(telegram, message, user):
	if not check_response(message, 'yes'):
		send_to_user(telegram, message.chat.id, message.from_user.language_code, 'not_deleted')
		return

	user.deleted_at = datetime.datetime.utcnow()
	user.chat_id = None
	user.save()
	send_to_user(telegram, message.chat.id, message.from_user.language_code, 'delete_completed')


@wrap_user_exists
def handler_in_conversation(telegram, message, user):
	# seach for last Conversation also active.

	conversation = ConversationModel.objects(Q(users__in=user.id) & \
											 Q(completed=False) & \
											 Q(users_size=2)
											 ).first()

	if not conversation:
		send_to_user(telegram, message.chat.id, message.from_user.language_code,
					 'conversation_stopped_by_other_geostranger')
		return

	for u in conversation.users:
		if u.id == user.id:
			continue
		break

	other_user = UserModel.objects(id=u)

	inline_keyboard = types.InlineKeyboardMarkup()

	inline_keyboard.add(trans_message(message.from_user.language_code, 'stop_talk_with_geostranger'))
	inline_keyboard.add(
		types.InlineKeyboardButton(trans_message(message.from_user.language_code, 'find_new_geostranger')))
	send_to_user(telegram, other_user.chat_id, )


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


@wrap_user_exists
def command_search(telegram, message, actual_user):
	# TODO: controlla se l'utente è ancora in coversazione, altrimenti esegui il command_stop.

	send_to_user(telegram, message.chat.id, message.from_user.language_code, 'in_search')

	user_found = search_user_near(actual_user)
	if not user_found:
		# TODO: Simple send message with text and inline buttons, (search again) if clicked, change text.
		return

	conversation = ConversationModel(users=[actual_user, user_found])
	conversation.save()

	if actual_user.first_time_chat:
		send_to_user(telegram, message.chat.id, message.from_user.language_code, 'found_new_geostranger_first_time',
					 handler=handler_in_conversation)
	else:

		send_to_user(telegram, user_found.user_id, user_found.language, 'found_new_geostranger',
					 handler=handler_in_conversation)


	"""Invia il messaggio al utente selezionato? """
	send_to_user(telegram, user_found.user_id, user_found.language, 'found_new_geostranger',
				 handler=handler_in_conversation)


@wrap_user_exists
def command_stop(telegram, message, user):
	user.chat_with = None
	user.save()

	send_to_user(telegram, message.chat.id, message.from_user.language_code, 'stop')


@wrap_user_exists
def command_delete_ask(telegram, message, user):
	markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
	markup.add(trans_message(message.from_user.language_code, 'yes'),
			   trans_message(message.from_user.language_code, 'no'))
	send_to_user(telegram, message.chat.id, message.from_user.language_code, 'delete_sure', reply_markup=markup,
				 handler=handler_delete)


def command_notify(telegram, message):
	send_to_user(telegram, message.chat.id, message.from_user.language_code, 'ask_notify', handler=handler_notify)


def command_start(telegram, message):
	actual_user = UserModel.objects(chat_type=telegram.chat_type, user_id=str(message.from_user.id),
									completed=True).first()
	if not actual_user:
		user = UserModel(chat_type=telegram.chat_type, user_id=str(message.from_user.id),
						 language=message.from_user.language_code)
		user.save()

		send_to_user(telegram, message.chat.id, message.from_user.language_code, 'start')
		send_to_user(telegram, message.chat.id, message.from_user.language_code, 'ask_location',
					 handler=handler_position_step1)

		return

	_search_for_new_chat_near_user(telegram, message, actual_user)


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
	@wrap_user_exists
	def execute(*args, **kwargs):
		command_stop(*args, **kwargs)

	@telegram.message_handler(commands=['delete'])
	@wrap_telegram(telegram)
	@wrap_exceptions
	@wrap_user_exists
	def execute(*args, **kwargs):
		command_delete_ask(*args, **kwargs)

	@telegram.message_handler(commands=['notify'])
	@wrap_telegram(telegram)
	@wrap_exceptions
	@wrap_user_exists
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
