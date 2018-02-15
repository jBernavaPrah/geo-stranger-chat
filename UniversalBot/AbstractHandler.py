# coding=utf-8
import datetime
import hashlib
import importlib
import logging
import mimetypes
import os
from abc import ABC, abstractmethod
from urllib.parse import urlparse

import requests
from flask import url_for
from flask_babel import gettext, force_locale
from geopy import Nominatim
from mongoengine import Q, DoesNotExist

import config
from UniversalBot.languages import lang
from UniversalBot.languages.lang import messages_to_not_botting
from models import ConversationModel, ProxyUrlModel
from utilities.mailer import send_mail_to_admin


class FileDownloadError(Exception):
	pass


class Abstract(ABC):
	_service = None

	@abstractmethod
	def expire_after_seconds(self, message):
		return 3600 * 24

	@abstractmethod
	def get_conversation_id_from_message(self, message):
		return 0

	@abstractmethod
	def get_user_language_from_message(self, message):
		return ''

	@abstractmethod
	def get_attachments_url_from_message(self, message):
		return []

	@abstractmethod
	def get_text_from_message(self, message):
		return ''

	@abstractmethod
	def new_keyboard(self, *args):
		return []

	@abstractmethod
	def remove_keyboard(self):
		pass

	@abstractmethod
	def bot_send_text(self, user_model, text, keyboard=None):
		raise NotImplemented

	@abstractmethod
	def bot_send_attachment(self, user_model, file_url, content_type, keyboard=None):
		raise NotImplemented

	@abstractmethod
	def is_group(self, message):
		raise NotImplemented

	@abstractmethod
	def can_continue(self, message):
		raise NotImplemented

	@abstractmethod
	def is_compatible(self, message):
		raise NotImplemented

	@abstractmethod
	def extract_message(self, request):
		raise NotImplemented

	@abstractmethod
	def get_extra_data(self, message):
		return None

	@abstractmethod
	def need_rewrite_commands(self):
		return False


class Handler(Abstract):

	@property
	def list_commands(self):

		if self._commands:
			return self._commands

		for x in dir(self):
			if x.endswith('_command'):
				self._commands.append(x.replace('_command', ''))

		return self._commands

	def __init__(self, request=None):

		self._commands = []

		self.current_conversation = None
		self.message_text = ''
		self.message_attachments = []
		self._need_rewrite = False

		self._actual_message = None

		if request:

			messages = self.extract_message(request)

			if isinstance(messages, (list, tuple)) or (
					hasattr(messages, '__iter__') and not isinstance(messages, dict)):
				for message in messages:
					self._process_message(message)

			else:
				self._process_message(messages)

	def _process_message(self, message):

		self._actual_message = message

		self._get_conversation_from_message(message)

		self._refresh_expire(message)

		if not self.can_continue(message):
			return

		if not self.is_compatible(message):
			self.not_compatible()
			return

		if self.is_group(message):
			# TODO: Response with correct item?
			return

		if not self._is_user_allowed():
			pass

		self.message_text = self.get_text_from_message(message)
		try:
			self.message_attachments = self.get_attachments_url_from_message(message)
		except FileDownloadError:
			self._internal_send_text(self.current_conversation, self.translate('download_file_error'), keyboard=self.remove_keyboard())

		self.generic_command()

	def _is_user_allowed(self):
		return True

	def _refresh_expire(self, message):
		seconds = self.expire_after_seconds(message)
		if seconds:
			self.current_conversation.expire_at = datetime.datetime.utcnow() + datetime.timedelta(seconds=seconds)
			self.current_conversation.save()

	@staticmethod
	def _registry_handler(user_model, handler_name):

		if hasattr(handler_name, '__name__'):
			handler_name = handler_name.__name__
		try:
			user_model.modify(next_function=handler_name)
		except DoesNotExist as e:
			logging.warning(e)

	def _get_conversation_from_message(self, message):
		conversation_id = self.get_conversation_id_from_message(message)

		self.current_conversation = self._get_conversation(self.__class__.__name__, conversation_id, False)

		if not self.current_conversation:
			extra_data = self.get_extra_data(message)
			conversation_id = self.get_conversation_id_from_message(message)
			language = self.get_user_language_from_message(message)

			self.current_conversation = ConversationModel(chat_type=str(self.__class__.__name__),
														  conversation_id=str(conversation_id),
														  language=language, extra_data=extra_data)
			self.current_conversation.save()

	@staticmethod
	def _get_mimetype(url):

		# TODO: do a head to url if no mimetypes given by extension!

		# url = 'https://webchat.botframework.com/attachments/FSwuL5g77fPGefKmk280n9/0000025/0/RETRIBUZIONIRELATIVEALCORRENTEANNO.pdf?t=ddKbtD8p354.dAA.RgBTAHcAdQBMADUAZwA3ADcAZgBQAEcAZQBmAEsAbQBrADIAOAAwAG4AOQAtADAAMAAwADAAMAAyADUA.X982jTec0wE.7Iwg-WuAW5w.QUelqWJcqB280Dpd38Iw88xMK0dm2UBM-g-0b5aIaeM'
		p = urlparse(url)
		m = mimetypes.guess_type(p.path)[0]

		if not m:
			# Not do a HEAD because kik return 400 bad request.
			with requests.get(url, stream=True) as r:
				m = r.headers['content-type']

		return m

	def _rewrite_commands(self, text):
		if self.need_rewrite_commands():
			if isinstance(text, (list, tuple)):
				for (i, item) in enumerate(text):
					if item[1:] in self.list_commands:
						text[i] = item.replace('/' + item[1:], '!' + item[1:])
				return text

			for command in self.list_commands:
				text = text.replace('/' + command, '!' + command)
		return text

	def _translate(self, text, **variables):
		if self.current_conversation and self.current_conversation.language:
			with force_locale(self.current_conversation.language):
				text = gettext(text, **variables)

				return text

		text = gettext(text, **variables)
		return text

	def translate(self, original_text, **variables):

		text = lang.bot_messages.get(original_text, original_text)
		text = self._translate(text, **variables)

		if original_text in messages_to_not_botting:
			return text

		return '*Bot:* ' + text

	@staticmethod
	def _md5(_str):

		return hashlib.md5((config.SECRET_KEY + _str).encode()).hexdigest()

	@staticmethod
	def _get_conversation(chat_type, conversation_id, strict=True):

		user = ConversationModel.objects(Q(chat_type=str(chat_type)) & \
										 Q(conversation_id=str(conversation_id)) & \
										 Q(deleted_at=None)) \
			.first()

		if not user and strict:
			logging.exception('User required, but not found.')
			raise RuntimeError

		return user

	def _check_response(self, check, strict=False):

		if not self.message_text:
			return False

		w = self.translate(check)

		if not strict:
			return self.message_text.lower().strip() == w.lower().strip()

		return self.message_text == w

	@staticmethod
	def _get_sender(sender_class, with_user):
		mod = importlib.import_module('UniversalBot')
		cls = getattr(mod, sender_class)()
		cls.current_conversation = with_user
		return cls

	@staticmethod
	def _secure_download(file_url, content_type=None):
		proxy = ProxyUrlModel(url=file_url, content_type=content_type).save()

		if not content_type:
			path = urlparse(file_url).path
			ext = os.path.splitext(path)[1]
		else:
			ext = '.' + content_type.split('/')[1]

		return url_for('index.download_action', _id=str(proxy.id) + str(ext), _external=True, _scheme='https')

	@staticmethod
	def _url_play_audio(file_url):
		proxy = ProxyUrlModel(url=file_url).save()
		return url_for('index.audio_page', _id=proxy.id, _external=True, _scheme='https')

	@staticmethod
	def _url_play_video(file_url):
		proxy = ProxyUrlModel(url=file_url).save()
		return url_for('index.video_page', _id=proxy.id, _external=True, _scheme='https')

	def _select_keyboard(self, user_model):

		# TODO: need to bee only see in some situations. Not always.

		commands = ['/terms', '/help', '/delete']

		if user_model.completed:
			commands = ['/new', '/location', '/terms', '/help', '/delete']

		if user_model.chat_with_exists:
			commands = ['/new', '/stop']

		commands = self._rewrite_commands(commands)

		return self.new_keyboard(*commands)

	def _internal_send_attachment(self, user_model, file_url, keyboard=None):

		if user_model.deleted_at:
			return False

		sender = self
		if self.__class__.__name__ != user_model.chat_type:
			sender = self._get_sender(user_model.chat_type, user_model)

		if not keyboard:
			keyboard = sender._select_keyboard(user_model)

		# TODO: Secure url
		content_type = self._get_mimetype(file_url)
		secure_url = self._secure_download(file_url, content_type)

		try:
			sender.bot_send_attachment(user_model, secure_url, content_type, keyboard=keyboard)
			return True
		except Exception as e:
			logging.debug(e)
			return False

	def _internal_send_text(self, user_model, text, keyboard=None):

		if user_model.deleted_at:
			return False

		sender = self
		if self.__class__.__name__ != user_model.chat_type:
			sender = self._get_sender(user_model.chat_type, user_model)

		if keyboard is None:
			keyboard = sender._select_keyboard(user_model)

		text = sender._rewrite_commands(text)

		try:
			sender.bot_send_text(user_model, text, keyboard=keyboard)
			return True
		except Exception as e:
			logging.debug(e)
			return False

	def not_compatible(self):
		if self.current_conversation:
			self._internal_send_text(self.current_conversation, self.translate('not_compatible'))

	def start_command(self):
		return self.welcome_command()

	def generic_command(self):

		logging.debug('Entering into Generic Command')
		# logging.debug('Message: \n\n%s' % json.dumps(message, indent=2, default=str))

		logging.debug('Conversation: %s ' % str(self.current_conversation.id))

		# logging.debug('Text with message: %s (len: %s)' % (str(execute_command), len(str(execute_command))))

		# logging.debug('User next_function: %s ' % str(self.current_conversation.next_function))
		if self.current_conversation.next_function:
			next_f = self.current_conversation.next_function
			self.current_conversation.next_function = None
			self.current_conversation.save()
			try:
				logging.debug('Executing function: %s ' % str(next_f))
				getattr(self, next_f)()
			except Exception as e:
				logging.exception(e)
				self._internal_send_text(self.current_conversation, self.translate('error'))
				self._registry_handler(self.current_conversation, self.current_conversation.next_function)

			return

		if not self.current_conversation.completed:
			logging.debug('Conversation not completed')
			self.welcome_command()
			return

		if self.message_text and len(self.message_text) and (
				self.message_text[0] == '/' or self.message_text[0] == '!'):

			logging.debug('Text (%s) is a command' % str(self.message_text.encode('utf-8')))
			# logging.debug('Text (%s) is a command' % execute_command)

			command = self.message_text[1:].strip()

			# annullo l'ultimo comando..
			next_f = self.current_conversation.next_function
			if next_f:
				logging.debug('Delete next_function of user (%s) ' % str(next_f))
				self.current_conversation.next_function = None
				self.current_conversation.save()

			if not hasattr(self, str(command) + '_command'):
				self._internal_send_text(self.current_conversation,
										 self.translate('command_not_found', command_text=command))
				return

			logging.debug('Executing command')
			try:
				getattr(self, str(command) + '_command')()
				return
			except Exception as e:
				logging.exception(e)
				self.current_conversation.next_function = next_f
				self.current_conversation.save()

				self._internal_send_text(self.current_conversation, self.translate('error'))

				return

		try:
			# Qua deve andare in errore in quanto mi devo disabilitare l'utente in caso.
			if self.current_conversation.chat_with:
				self.__proxy_message()
				return
		except DoesNotExist:

			self.current_conversation.chat_with = None
			self.current_conversation.save()

			self._internal_send_text(self.current_conversation, self.translate('stop'))
			return

		""" Proxy the message to other user """

		self.help_command()

	def welcome_command(self):

		self._internal_send_text(self.current_conversation, self.translate('welcome'), keyboard=self.remove_keyboard())

		if not self.current_conversation.location or not self.current_conversation.completed:
			self.location_command()
			return

		"""User is completed, need a search or change the location?"""
		self.__engage_users()

	def location_command(self):

		self._internal_send_text(self.current_conversation, self.translate('ask_location'),
								 keyboard=self.remove_keyboard())
		self._registry_handler(self.current_conversation, self._handler_location_step1)

	def delete_command(self):
		self._internal_send_text(self.current_conversation, self.translate('ask_delete_sure'),
								 keyboard=self.new_keyboard(self.translate('yes'), self.translate('no')))
		self._registry_handler(self.current_conversation, self._handle_delete_step1)

	def terms_command(self):

		self._internal_send_text(self.current_conversation,
								 self.translate('terms',
												terms_url=url_for('index.terms_page', _external=True, _scheme='https')))

	def help_command(self):
		self._internal_send_text(self.current_conversation, self.translate('help'))

	def notify_command(self):
		self._internal_send_text(self.current_conversation, self.translate('ask_notify'))
		self._registry_handler(self.current_conversation, self._handle_notify_step1)

	def stop_command(self):

		yes_no_keyboard = self.new_keyboard(self.translate('yes'), self.translate('no'))

		if self.current_conversation.chat_with_exists:
			self._internal_send_text(self.current_conversation,
									 self.translate('ask_stop_also_current_chat'),
									 keyboard=yes_no_keyboard)
			self._registry_handler(self.current_conversation, self._handle_stop_step1)
			return

		self._internal_send_text(self.current_conversation,
								 self.translate('ask_stop_sure'), keyboard=yes_no_keyboard)
		self._registry_handler(self.current_conversation, self._handle_stop_step1)

	def new_command(self):
		# I not need here retrieve all user info

		if not self.current_conversation.chat_with_exists:
			self.__engage_users()
			return

		self._internal_send_text(self.current_conversation,
								 self.translate('sure_search_new'),
								 keyboard=self.new_keyboard(self.translate('yes'),
															self.translate('no')))
		self._registry_handler(self.current_conversation, self._handle_new_step1)

	def _handle_new_step1(self):

		if not self._check_response('yes'):
			self._internal_send_text(self.current_conversation, self.translate('not_stopped'))
			return

		self.__stop_by_other_user()

		# Se non è uguale a None, vuol dire che è stato scelto da qualcun altro.. e allora non devo mica cercarlo.
		self.current_conversation = ConversationModel.objects(id=self.current_conversation.id,
															  chat_with=self.current_conversation.chat_with).modify(
			chat_with=None, new=True)

		if not self.current_conversation.chat_with_exists:
			self.__engage_users()

		return

	def _handle_stop_step1(self):

		if not self._check_response('yes'):
			self._internal_send_text(self.current_conversation, self.translate('not_stopped'))
			return

		self.__stop_by_other_user()

		self.current_conversation = ConversationModel.objects(id=self.current_conversation.id,
															  chat_with=self.current_conversation.chat_with).modify(
			chat_with=None,
			is_searchable=False, new=True)
		self._internal_send_text(self.current_conversation, self.translate('stop'))

	def _handle_delete_step1(self):

		if not self._check_response('yes'):
			self._internal_send_text(self.current_conversation, self.translate('not_deleted'))
			return

		self.current_conversation.deleted_at = datetime.datetime.utcnow()
		self.current_conversation.save()
		self._internal_send_text(self.current_conversation, self.translate('delete_completed'))

	def _handler_location_step1(self):

		if not self.message_text:
			self._internal_send_text(self.current_conversation, self.translate('location_error'),
									 keyboard=self.remove_keyboard())
			self._registry_handler(self.current_conversation, self._handler_location_step1)
			return

		geolocator = Nominatim()
		location = geolocator.geocode(self.message_text, language=self.current_conversation.language)

		if not location:
			""" Location non trovata.. """
			self._internal_send_text(self.current_conversation, self.translate('location_not_found',
																			   location_text=self.message_text),
									 keyboard=self.remove_keyboard())
			self._registry_handler(self.current_conversation, self._handler_location_step1)
			return

		""" Location trovata! Per il momento la salvo e chiedo se è corretta :) """
		self.current_conversation.location = [location.longitude, location.latitude]
		self.current_conversation.location_text = location.address
		self.current_conversation.save()

		self._internal_send_text(self.current_conversation,
								 self.translate('ask_location_is_correct', location_text=location.address),
								 keyboard=self.new_keyboard(self.translate('yes'), self.translate('no')))
		self._registry_handler(self.current_conversation, self._handler_location_step2)

	def _handler_location_step2(self):

		if not self._check_response('yes'):
			""" Richiedo allora nuovamente la posizione """

			self._internal_send_text(self.current_conversation, self.translate('re_ask_location'),
									 keyboard=self.remove_keyboard())
			self._registry_handler(self.current_conversation, self._handler_location_step1)
			return

		self._internal_send_text(self.current_conversation, self.translate('location_saved',
																		   location_text=self.current_conversation.location_text),
								 keyboard=self.remove_keyboard())

		""" Location ok! """

		if not self.current_conversation.completed:
			self.current_conversation.completed = True
			self.current_conversation.save()
			self._internal_send_text(self.current_conversation, self.translate('completed'))

	def _handle_notify_step1(self):
		send_mail_to_admin('notify_from_bot', MESSAGE=self.message_text)
		self._internal_send_text(self.current_conversation, self.translate('notify_sent'))

	def __stop_by_other_user(self):

		# Devo disabilitare anche il search, in maniera tale che l'utente b clicchi su Search se vuole ancora cercare.
		# Questo mi permette di eliminare il problema webchat..
		# ---------
		# Ora la webchat viene gestita tramite un expire_at, aggiornato ad ogni messaggio pervenuto da quel conversation_id

		try:
			# Nel caso l'utnete non esiste più (viene caricato quando accedo a reference chat_with) allora non serve che effettuo invii
			notify_user = self.current_conversation.chat_with
			notify_user = ConversationModel.objects(id=notify_user.id, chat_with=self.current_conversation).modify(
				chat_with=None,
				new=True)

			self._internal_send_text(notify_user, self.translate('conversation_stopped_by_other_geostranger'))
		except DoesNotExist:
			# todo: ATOMICAMENTE!
			self.current_conversation.chat_with = None
			self.current_conversation.save()
			return

	def __engage_users(self):

		self._internal_send_text(self.current_conversation, self.translate('in_search'),
								 keyboard=self.remove_keyboard())

		if not self.current_conversation.is_searchable:
			self.current_conversation.is_searchable = True
			self.current_conversation.save()

		# L'utente fa il search. Posso utilizzarlo solamente se l'utente non è al momento sotto altra conversation.
		# Questo vuol dire che non devo fare nessun ciclo. E' UNA FUNZIONE ONE SHOT!
		# E se non trovo nulla, devo aspettare che sia un altro a fare questa operazione e "Trovarmi"..

		# http://docs.mongoengine.org/guide/querying.html#further-aggregation

		exclude_users = [self.current_conversation.id]

		# Now all search are with meritocracy!
		# Order users in bases of distance, Last engage, messages received and sent, and when are created.
		conversation_found = ConversationModel.objects(Q(id__nin=exclude_users) & \
													   Q(chat_with=None) & \
													   (Q(is_searchable=True) | Q(allow_search=True)) & \
													   Q(completed=True) & \
													   Q(location__near=self.current_conversation.location) & \
													   (Q(expire_at__exists=False) | Q(
														   expire_at__gte=datetime.datetime.utcnow()))) \
			.order_by("+created_at") \
			.order_by("+messages_sent") \
			.order_by("+messages_received") \
			.order_by("+last_engage_at") \
			.modify(chat_with=self.current_conversation,
					last_engage_at=datetime.datetime.utcnow(),
					new=True)

		""" Memurandum: Il più vuol dire crescendo (0,1,2,3) il meno vuol dire decrescendo (3,2,1,0) """
		""" Memurandum: Prima ordino per quelli meno importanti, poi per quelli più importanti """

		""" Se non ho trovato nessuno, devo solo aspettare che il sistema mi associ ad un altro geostranger. """
		if not conversation_found:
			self._internal_send_text(self.current_conversation, self.translate('search_not_found'))

			""" Se non ho trovato nulla e non sono stato selezionato, aspetto.. succederà prima o poi :) """
			return

		logging.debug('Found %s user' % str(conversation_found.id))

		actual_user = ConversationModel.objects(id=self.current_conversation.id,
												chat_with=None) \
			.modify(chat_with=conversation_found,
					last_engage_at=datetime.datetime.utcnow(),
					new=True)

		if not actual_user:
			""" Se sono già stato scelto durante questa query, allora semplicemente effettuo il release del utente.  """
			ConversationModel.objects(id=conversation_found.id, chat_with=actual_user).modify(chat_with=None)
			return

		"""Invia il messaggio al utente selezionato """

		if conversation_found.first_time_chat:
			send_text = 'found_new_geostranger_first_time'
		else:
			send_text = 'found_new_geostranger'

		sent = self._internal_send_text(conversation_found,
										self.translate(send_text, location_text=actual_user.location_text))

		if not sent:
			""" il messaggio non è stato inviato.. probabilmente l'utente non è più disponibile, provvedo a togliere le associazioni"""
			actual_user = ConversationModel.objects(id=actual_user.id, chat_with=conversation_found).modify(
				chat_with=None, new=True)
			conversation_found = ConversationModel.objects(id=conversation_found.id, chat_with=actual_user).modify(
				chat_with=None, new=True)

			return

		self._internal_send_text(conversation_found, self.translate('new_chat'))

		if conversation_found.first_time_chat:
			conversation_found.first_time_chat = False
			conversation_found.save()

		if actual_user.first_time_chat:
			send_text = 'found_new_geostranger_first_time'
		else:
			send_text = 'found_new_geostranger'

		self._internal_send_text(actual_user, self.translate(send_text, location_text=conversation_found.location_text))
		self._internal_send_text(actual_user, self.translate('new_chat'))

		if actual_user.first_time_chat:
			actual_user.first_time_chat = False
			actual_user.save()

	# LastChatsModel(from_user=actual_user, to_user=user_found).save()
	# LastChatsModel(from_user=user_found, to_user=actual_user).save()

	def __proxy_message(self):

		logging.debug('Proxy the message from ConversationModel(%s) to ConversationModel(%s)' % (
			self.current_conversation.id, self.current_conversation.chat_with.id))

		# TODO: If conversation return false, then need to stop it!

		self.current_conversation.update(inc__messages_sent=1)
		self.current_conversation.chat_with.update(inc__messages_received=1)

		if len(self.message_attachments):
			for attachment_url in self.message_attachments:
				self._internal_send_attachment(self.current_conversation.chat_with, attachment_url)

		if self.message_text:
			self._internal_send_text(self.current_conversation.chat_with, self.message_text)
