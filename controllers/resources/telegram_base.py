# coding=utf-8
import json
import logging
from functools import wraps

from geopy.geocoders import Nominatim

import datetime
from mongoengine.queryset.visitor import Q

from controllers.resources.languages import trans_message as _
from models import UserModel, MessageModel
from telebot import types


# WRAPPERS #


def wrap_user_exists(strict=True):
	def x(func):
		@wraps(func)
		def call(telegram, message, user=None, *args, **kwargs):

			# In questa maniera posso gestire anche il richiamo diretto da funzione interna.
			if not isinstance(user, UserModel):
				user = UserModel.objects(Q(chat_type=telegram.chat_type) & \
										 Q(user_id=str(message.from_user.id)) & \
										 Q(deleted_at=None)) \
					.first()

			if not user and strict:
				logging.exception('User required, but not found.')
				raise RuntimeError

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
				send_message(telegram, message.from_user.id, message.from_user.language_code, 'error')

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




def send_message(telegram, user_id, lang, what, handler=None, reply_markup=None, format_with=None, *args, **kwargs):
	msg = telegram.send_message(user_id,
								_(lang, what, format_with),
								parse_mode='markdown', reply_markup=reply_markup, *args, **kwargs)

	"""Registry handler"""
	registry_handler(telegram, user_id, handler, msg.message_id)

	return msg


def reply_to(telegram, message, what, format_with=None, *args, **kwargs):
	return telegram.reply_to(message, _(message.from_user.language_code, what, format_with),
							 parse_mode='markdown', *args, **kwargs)


def edit_message_text(telegram, user_id, message_id, lang, what, format_with=None, handler=None, reply_markup=None,
					  *args,
					  **kwargs):
	msg = telegram.edit_message_text(_(lang, what, format_with),
									 user_id, message_id,
									 parse_mode='markdown', reply_markup=reply_markup, *args,
									 **kwargs)
	"""Registry handler"""
	registry_handler(telegram, user_id, handler, msg.message_id)
	return msg


def check_response(telegram, message, what, strict=False):
	m = None

	if hasattr(message, 'text'):
		m = message.text

	if hasattr(message, 'data'):
		m = message.data

	if message.change_message_id:
		markup = types.InlineKeyboardMarkup()
		# markup.add(types.InlineKeyboardButton(_(message.from_user.language_code, 'thanks')))
		telegram.edit_message_reply_markup(message.from_user.id, message_id=message.change_message_id,
										   reply_markup=markup)

	if not m:
		return False

	w = _(message.from_user.language_code, what)

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

		send_message(telegram, message.from_user.id, message.from_user.language_code, 'completed')

		return

	location_text = message.text.encode('utf8').strip()

	if not location_text:
		send_message(telegram, message.from_user.id, message.from_user.language_code, 'location_error',
					 handler=handler_position_step1)
		return

	geolocator = Nominatim()
	location = geolocator.geocode(location_text, language=message.from_user.language_code)

	if not location:
		""" Location non trovata.. """
		send_message(telegram, message.from_user.id, message.from_user.language_code, 'location_not_found',
					 handler=handler_position_step1,
					 format_with={'location_text': location_text})
		return

	""" Location trovata! Per il momento la salvo e chiedo se è corretta :) """
	user.location = [location.longitude, location.latitude]
	user.location_text = location.address
	user.save()

	markup = types.InlineKeyboardMarkup()
	markup.add(types.InlineKeyboardButton(_(message.from_user.language_code, 'yes'),
										  callback_data=_(message.from_user.language_code, 'yes')))
	markup.add(types.InlineKeyboardButton(_(message.from_user.language_code, 'no'),
										  callback_data=_(message.from_user.language_code, 'no')))

	edit_message_text(telegram, message.from_user.id, message.change_message_id, message.from_user.language_code,
					  'ask_location_is_correct',
					  reply_markup=markup, handler=handler_position_step2,
					  format_with={'location_text': location.address})


def handler_position_step2(telegram, message, user):
	if not check_response(telegram, message, 'yes'):
		""" Richiedo allora nuovamente la posizione """
		send_message(telegram, message.from_user.id, message.from_user.language_code, 're_ask_location',
					 handler=handler_position_step1)
		return

	edit_message_text(telegram, message.from_user.id, message.change_message_id, message.from_user.language_code,
					  'location_saved', format_with={'location_text': user.location_text})

	""" Location ok! """
	# send_to_user(telegram, message.from_user.id, message.from_user.language_code, 'ask_age', handler=handler_age_step)
	user.completed = True
	user.save()
	send_message(telegram, message.from_user.id, message.from_user.language_code, 'completed')


def handler_stop(telegram, message, user):
	if not check_response(telegram, message, 'yes'):
		edit_message_text(telegram, message.from_user.id, message.change_message_id, message.from_user.language_code,
						  'not_stopped')
		return

	if user.chat_with:
		send_message(telegram, user.chat_with.user_id, user.chat_with.language,
					 'conversation_stopped_by_other_geostranger')

		user.chat_with.chat_with = None
		user.chat_with.save()

	user.chat_with = None
	user.allow_search = False
	user.save()

	edit_message_text(telegram, message.from_user.id, message.change_message_id, message.from_user.language_code,
					  'stop')


def handler_delete(telegram, message, user):
	if not check_response(telegram, message, 'yes'):
		send_message(telegram, message.from_user.id, message.from_user.language_code, 'not_deleted')
		return

	user.deleted_at = datetime.datetime.utcnow()
	user.save()
	send_message(telegram, message.from_user.id, message.from_user.language_code, 'delete_completed')


def handler_notify(telegram, message):
	message.text.encode('utf-8').strip()
	send_message(telegram, message.from_user.id, message.from_user.language_code, 'notify_sent')


# END HANDLERS #


# COMMAND #


def command_terms(telegram, message):
	send_message(telegram, message.from_user.id, message.from_user.language_code, 'terms')


def command_help(telegram, message):
	help_text = ''
	for key in telegram.commands:  # generate help text out of the commands dictionary defined at the top
		help_text += "/" + telegram.commands[key] + ": "
		help_text += _(message.from_user.language_code, 'command_' + telegram.commands[key]) + "\n"

	send_message(telegram, message.from_user.id, message.from_user.language_code, 'help',
				 format_with={'help_text': help_text})


@wrap_user_exists()
def command_search(telegram, message, actual_user):
	# controlla se l'utente non è in coversazione, altrimenti esegui il command_stop.
	if actual_user.chat_with:
		command_stop(telegram, message, actual_user)
		return
	"""Per evitare di scrivere troppe volte in db"""
	if not actual_user.allow_search:
		actual_user.allow_search = True
		actual_user.save()

	msg = send_message(telegram, message.from_user.id, message.from_user.language_code, 'in_search')

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

	actual_user.chat_with = user_found
	actual_user.save()

	au_tx = 'found_new_geostranger_first_time' if actual_user.first_time_chat else 'found_new_geostranger'

	edit_message_text(telegram, message.from_user.id, msg.message_id, message.from_user.language_code, au_tx,
					  format_with={'location_text': user_found.location_text})
	if actual_user.first_time_chat:
		actual_user.first_time_chat = False
		actual_user.save()

	"""Invia il messaggio al utente selezionato """

	uf_tx = 'found_new_geostranger_first_time' if user_found.first_time_chat else 'found_new_geostranger'
	send_message(telegram, user_found.user_id, user_found.language, uf_tx,
				 format_with={'location_text': actual_user.location_text})
	if user_found.first_time_chat:
		user_found.first_time_chat = False
		user_found.save()


@wrap_user_exists()
def command_stop(telegram, message, user):
	# This will also stop receiving new geostrangers. To reactive send /search.

	# Are you sure to stop messaging?

	markup = types.InlineKeyboardMarkup()
	markup.add(types.InlineKeyboardButton(_(message.from_user.language_code, 'yes'),
										  callback_data=_(message.from_user.language_code, 'yes')))
	markup.add(types.InlineKeyboardButton(_(message.from_user.language_code, 'no'),
										  callback_data=_(message.from_user.language_code, 'no')))

	if user.chat_with:
		send_message(telegram, user.user_id, user.language, 'ask_stop_also_current_chat', reply_markup=markup,
					 handler=handler_stop)
	else:
		send_message(telegram, user.user_id, user.language, 'ask_stop_sure', reply_markup=markup, handler=handler_stop)


@wrap_user_exists(True)
def command_delete(telegram, message, user):
	markup = types.InlineKeyboardMarkup()
	markup.add(types.InlineKeyboardButton(_(message.from_user.language_code, 'yes'),
										  callback_data=_(message.from_user.language_code, 'yes')))
	markup.add(types.InlineKeyboardButton(_(message.from_user.language_code, 'no'),
										  callback_data=_(message.from_user.language_code, 'no')))

	send_message(telegram, message.from_user.id, message.from_user.language_code, 'ask_delete_sure',
				 reply_markup=markup,
				 handler=handler_delete)


def command_notify(telegram, message):
	send_message(telegram, message.from_user.id, message.from_user.language_code, 'ask_notify', handler=handler_notify)


@wrap_user_exists(False)
def command_start(telegram, message, user):
	if not user:
		user = UserModel(chat_type=telegram.chat_type, user_id=str(message.from_user.id),
						 language=message.from_user.language_code)
		user.save()
		send_message(telegram, message.from_user.id, message.from_user.language_code, 'welcome')

	if not user.location:
		command_location(telegram, message, user)
		return

	"""User is completed, need a seach or change the location?"""
	send_message(telegram, message.from_user.id, message.from_user.language_code, 'search')


@wrap_user_exists()
def command_location(telegram, message, user):
	""" Se la location è già presente... La tua locazione al momento é: Vuoi cambiarla? Si no (inline button)"""

	send_message(telegram, message.from_user.id, message.from_user.language_code, 'ask_location',
				 handler=handler_position_step1)


@wrap_user_exists(False)
def command_handler(telegram, message, user):
	if not user or (not user.chat_with and not user.next_function):
		command_start(telegram, message, user)
		return

	if user.next_function:
		try:

			next_f = user.next_function

			message.change_message_id = None

			if hasattr(message, 'message') and hasattr(message.message, 'message_id'):
				message.change_message_id = message.message.message_id

			if '#' in user.next_function:
				next_f, change_message_id = user.next_function.split('#')
				message.change_message_id = int(change_message_id)

			return globals()[next_f](telegram, message, user)
		except Exception as e:
			logging.exception(e)
			registry_handler(telegram, message.from_user.id, user.next_function)
			return

	if not user.chat_with:
		send_message(telegram, message.from_user.id, message.from_user.language_code,
					 'conversation_stopped_by_other_geostranger')
		return


	m = MessageModel(user=user)



	reply_to_message_id = None
	if hasattr(message.reply_to_message, 'message_id'):
		reply_to_message_id = message.reply_to_message.message_id - 1

	if message.text:
		m.text = message.text
		m.save()

		telegram.send_message(user.chat_with.user_id, '*GeoStranger:* ' + message.text,
							  parse_mode='markdown', reply_to_message_id=reply_to_message_id)

	caption = "GeoStranger" + ': ' + message.caption if message.caption else ''

	files = ['audio', 'document', 'sticker', 'video', 'video_note', 'voice']

	for f in files:

		_f = getattr(message, f)

		if _f is not None:
			file_info = telegram.get_file(_f.file_id)
			m.document.put(telegram.download_file(file_info.file_path),
						   metadata=json.dumps(_f.__dict__, default=str))
			m.save()
			getattr(telegram, 'send_%s' % f)(user.chat_with.user_id, _f.file_id, caption=caption,
											 reply_to_message_id=reply_to_message_id)
			break


	if message.photo:

		if isinstance(message.photo, (tuple, list)):
			selected_photo = message.photo[-1]
		else:
			selected_photo = message.photo

		file_info = telegram.get_file(selected_photo.file_id)
		m.photo.put(telegram.download_file(file_info.file_path))
		m.save()
		telegram.send_photo(user.chat_with.user_id, selected_photo.file_id, caption=caption,
							reply_to_message_id=reply_to_message_id)

	if message.location:
		m.location = [message.location.longitude, message.location.latitude]
		m.save()
		telegram.send_location(user.chat_with.user_id, message.location.latitude, message.location.longitude,
							   reply_to_message_id=reply_to_message_id)

	if message.contact:
		m.contact = message.contact.__dict__
		m.save()
		telegram.send_contact(user.chat_with.user_id, message.contact.phone_number, message.contact.first_name,
							  message.contact.last_name)


# raise e


def registry_handler(telegram, user_id, handler_name, message_id=None):
	""" Salvo un handler per l'utente. Potrò gestire le risposte direttamente nel software.
		message_id: mi serve per poter modificare il messaggio e non inviare uno nuovo ogni volta.
	"""
	if hasattr(handler_name, '__name__'):
		handler_name = handler_name.__name__
		if message_id:
			handler_name = '%s#%s' % (handler_name, str(message_id))

	UserModel.objects(chat_type=telegram.chat_type, user_id=str(user_id), deleted_at=None) \
		.modify(next_function=handler_name, upsert=True)


# END COMMAND #

# INLINE HANDLER #

def inline_handler(telegram, inline_query):
	print inline_query
	pass


# END INLINE HANDLER#

def message_handler(telegram):
	@telegram.callback_query_handler(lambda call: True)
	@wrap_telegram(telegram)
	@wrap_exceptions
	def execute(*args, **kwargs):
		command_handler(*args, **kwargs)

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
	def execute(*args, **kwargs):
		command_delete(*args, **kwargs)

	@telegram.message_handler(commands=['notify'])
	@wrap_telegram(telegram)
	@wrap_exceptions
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

	@telegram.message_handler(func=lambda message: True,
							  content_types=['text', 'audio', 'document', 'photo', 'sticker', 'video', 'video_note',
											 'voice', 'location', 'contact'])
	@wrap_telegram(telegram)
	@wrap_exceptions
	def execute(*args, **kwargs):
		command_handler(*args, **kwargs)
