# coding=utf-8
import datetime
import hashlib
import importlib
import logging
from abc import ABC, abstractmethod

from flask import url_for
from flask_babel import gettext, force_locale
from geopy import Nominatim
from mongoengine import Q, DoesNotExist

import config
from UniversalBot.languages import lang
from UniversalBot.languages.lang import messages_to_not_botting
from models import ConversationModel, ProxyUrlModel


class FileDownloadError(Exception):
	pass


class FileUploadError(Exception):
	pass


class KeyboardNotCompatible(Exception):
	pass


class Abstract(ABC):
	_service = None

	@abstractmethod
	def authorization(self):
		return None

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
	def have_keyboard(self, message):
		return True

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
		self._have_keyboard = True

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

		if not self.have_keyboard(message):
			self._have_keyboard = False

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
		self.message_attachments = self.get_attachments_url_from_message(message)
		self._check_attachment()

		self.generic_command()

	def _check_attachment(self):

		allowed_attachments = ['audio', 'video', 'image']
		all_ok = True
		for (i, item) in enumerate(self.message_attachments):

			if not item[0].startswith(tuple(allowed_attachments)):
				del self.message_attachments[i]
				all_ok = False

		if not all_ok:
			self._internal_send_text(self.current_conversation, self.translate('attachment_not_compatible',
																			   allowed_attachments=allowed_attachments),
									 commands=False)

	def _is_user_allowed(self):
		return True

	def _refresh_expire(self, message):
		seconds = self.expire_after_seconds(message)
		if seconds:
			self.current_conversation.expire_at = datetime.datetime.utcnow() + datetime.timedelta(seconds=seconds)
			self.current_conversation.save()
		else:
			if self.current_conversation.expire_at:
				self.current_conversation.expire_at = None
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
			conversation_id = self.get_conversation_id_from_message(message)
			language = self.get_user_language_from_message(message)

			self.current_conversation = ConversationModel(chat_type=str(self.__class__.__name__),
														  conversation_id=str(conversation_id),
														  language=language)
			self.current_conversation.save()

		extra_data = self.get_extra_data(message)
		if self.current_conversation.extra_data != extra_data:
			self.current_conversation.extra_data = extra_data
			self.current_conversation.save()

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
			language = self.current_conversation.language

			with force_locale(language[:2]):
				text = gettext(text, **variables)

				return text

		text = gettext(text, **variables)
		return text

	def translate(self, original_text, **variables):

		text = lang.bot_messages.get(original_text, original_text)
		text = self._translate(text, **variables)

		if original_text in messages_to_not_botting:
			return text

		return '🤖' + ' ' + text

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
	def _correct_content_type(file_type):

		_suffix = ''

		if file_type == 'image':
			_suffix = '/png'
		if file_type == 'audio':
			_suffix = '/mp3'
		if file_type == 'video':
			_suffix = '/mp4'

		return file_type + _suffix

	def _secure_download(self, file_url, file_type=None):

		proxy = ProxyUrlModel(url=file_url, file_type=file_type, headers=self.authorization()).save()

		return str(proxy.id)

	def _select_commands(self, user_model):

		# TODO: need to bee only see in some situations. Not always.

		commands = ['/terms', '/help', '/delete']

		if user_model.completed:
			commands = ['/new', '/location', '/terms', '/help', '/delete']

		if user_model.chat_with_exists:
			commands = ['/new', '/stop']

		return commands

	def _generate_keyboard(self, user_model, commands):
		if self._have_keyboard:

			if commands is None:
				commands = self._select_commands(user_model)

			if commands:
				commands = self._rewrite_commands(commands)
				return self.new_keyboard(*commands)

	def _internal_send_text(self, user_model, text, commands=None):

		if user_model.deleted_at:
			return False

		sender = self
		if self.__class__.__name__ != user_model.chat_type:
			sender = self._get_sender(user_model.chat_type, user_model)

		keyboard = sender._generate_keyboard(user_model, commands)

		text = sender._rewrite_commands(text)

		try:
			sender.bot_send_text(user_model, text, keyboard=keyboard)
			if not keyboard and commands:
				sender.bot_send_text(user_model, self.translate('commands_available', commands=commands))
			return True
		except Exception as e:
			# Need monitoring exceptions in this times!
			logging.exception(e)
			return False

	def _internal_send_attachment(self, user_model, attachment, commands=None):

		if user_model.deleted_at:
			return False

		sender = self
		if self.__class__.__name__ != user_model.chat_type:
			sender = self._get_sender(user_model.chat_type, user_model)

		keyboard = sender._generate_keyboard(user_model, commands)

		file_type = attachment[0]
		file_url = attachment[1]

		_id = self._secure_download(file_url, file_type)

		secure_url = url_for('index.download_action', _id=_id, _external=True, _scheme='https')

		try:
			sender.bot_send_attachment(user_model, secure_url, file_type, keyboard=keyboard)
			if not keyboard and commands:
				sender.bot_send_text(user_model, self.translate('commands_available', commands=commands))

			return True
		except Exception as e:

			logging.warning(e)

			if file_type and file_type.startswith('image'):
				secure_url = url_for('index.image_page', _id=_id, _external=True, _scheme='https')

				return self._internal_send_text(user_model, self.translate('show_image', file_url=secure_url),
												commands=commands)

			if file_type and file_type.startswith('video'):
				secure_url = url_for('index.video_page', _id=_id, _external=True, _scheme='https')

				return self._internal_send_text(user_model, self.translate('play_video', file_url=secure_url),
												commands=commands)

			if file_type and file_type.startswith('audio'):
				secure_url = url_for('index.audio_page', _id=_id, _external=True, _scheme='https')

				return self._internal_send_text(user_model, self.translate('play_audio', file_url=secure_url),
												commands=commands)

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

		self._internal_send_text(self.current_conversation, self.translate('welcome'), commands=False)

		if not self.current_conversation.location or not self.current_conversation.completed:
			self.location_command()
			return

		"""User is completed, need a search or change the location?"""
		self.__engage_users()

	def location_command(self):

		self._internal_send_text(self.current_conversation, self.translate('ask_location'), commands=False)
		self._registry_handler(self.current_conversation, self._handler_location_step1)

	def delete_command(self):
		self._internal_send_text(self.current_conversation, self.translate('ask_delete_sure'),
								 commands=[self.translate('yes'), self.translate('no')])
		self._registry_handler(self.current_conversation, self._handle_delete_step1)

	def terms_command(self):

		self._internal_send_text(self.current_conversation,
								 self.translate('terms',
												terms_url=url_for('index.terms_page', _external=True, _scheme='https')))

	def help_command(self):
		self._internal_send_text(self.current_conversation, self.translate('help'))

	def notify_command(self):
		self._internal_send_text(self.current_conversation, self.translate('notification', contact_us_url=url_for(
			'index.contact_us_page', _external=True, _scheme='https')))

	def stop_command(self):

		yes_no_keyboard = [self.translate('yes'), self.translate('no')]

		if self.current_conversation.chat_with_exists:
			self._internal_send_text(self.current_conversation,
									 self.translate('ask_stop_also_current_chat'),
									 commands=yes_no_keyboard)
			self._registry_handler(self.current_conversation, self._handle_stop_step1)
			return

		self._internal_send_text(self.current_conversation,
								 self.translate('ask_stop_sure'), commands=yes_no_keyboard)
		self._registry_handler(self.current_conversation, self._handle_stop_step1)

	def new_command(self):
		# I not need here retrieve all user info

		if not self.current_conversation.chat_with_exists:
			self.__engage_users()
			return

		self._internal_send_text(self.current_conversation,
								 self.translate('sure_search_new'),
								 commands=[self.translate('yes'), self.translate('no')])
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
			is_searchable=False, allow_search=False, new=True)
		self._internal_send_text(self.current_conversation, self.translate('stop'))

	def _handle_delete_step1(self):

		if not self._check_response('yes'):
			self._internal_send_text(self.current_conversation, self.translate('not_deleted'))
			return

		self._internal_send_text(self.current_conversation, self.translate('delete_completed'))

		self.current_conversation.deleted_at = datetime.datetime.utcnow()
		self.current_conversation.save()

	def _handler_location_step1(self):

		if not self.message_text:
			self._internal_send_text(self.current_conversation, self.translate('location_error'), commands=False)
			self._registry_handler(self.current_conversation, self._handler_location_step1)
			return

		geolocator = Nominatim()
		location = geolocator.geocode(self.message_text, language=self.current_conversation.language)

		if not location:
			""" Location non trovata.. """
			self._internal_send_text(self.current_conversation, self.translate('location_not_found',
																			   location_text=self.message_text),
									 commands=False)
			self._registry_handler(self.current_conversation, self._handler_location_step1)
			return

		""" Location trovata! Per il momento la salvo e chiedo se è corretta :) """
		self.current_conversation.location = [location.longitude, location.latitude]
		self.current_conversation.location_text = location.address
		self.current_conversation.save()

		self._internal_send_text(self.current_conversation,
								 self.translate('ask_location_is_correct', location_text=location.address),
								 commands=[self.translate('yes'), self.translate('no')])
		self._registry_handler(self.current_conversation, self._handler_location_step2)

	def _handler_location_step2(self):

		if not self._check_response('yes'):
			""" Richiedo allora nuovamente la posizione """

			self._internal_send_text(self.current_conversation, self.translate('re_ask_location'), commands=False)
			self._registry_handler(self.current_conversation, self._handler_location_step1)
			return

		self._internal_send_text(self.current_conversation, self.translate('location_saved',
																		   location_text=self.current_conversation.location_text),
								 commands=False)

		""" Location ok! """

		if not self.current_conversation.completed:
			self.current_conversation.completed = True
			self.current_conversation.save()
		self._internal_send_text(self.current_conversation, self.translate('completed'))

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

	def __engage_users(self, count=0):

		if not count:
			self._internal_send_text(self.current_conversation, self.translate('in_search'), commands=False)

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
													   Q(deleted_at=None) & \
													   Q(location__near=self.current_conversation.location) & \
													   (Q(expire_at__exists=False) | Q(
														   expire_at__gte=datetime.datetime.utcnow()))) \
			.order_by("+created_at") \
			.order_by("+messages_sent") \
			.order_by("+messages_received") \
			.order_by("+last_engage_at") \
			.modify(chat_with=self.current_conversation,
					last_engage_at=datetime.datetime.utcnow(),
					inc__chatted_times=1,
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
					inc__chatted_times=1,
					new=True)

		if not actual_user:
			""" Se sono già stato scelto durante questa query, allora semplicemente effettuo il release del utente.  """
			ConversationModel.objects(id=conversation_found.id, chat_with=actual_user).modify(chat_with=None,
																							  inc__chatted_times=-1)
			return

		"""Invia il messaggio al utente selezionato """

		if conversation_found.first_time_chat:
			send_text = 'found_new_geostranger_first_time'
		else:
			send_text = 'found_new_geostranger'

		sent = self._internal_send_text(conversation_found,
										self.translate(send_text, location_text=actual_user.location_text))

		if not sent:

			# TODO: Dopo aver resettato i contatori, posso ricercare di nuovo un nuova convesazione.

			""" il messaggio non è stato inviato.. probabilmente l'utente non è più disponibile, provvedo a togliere le associazioni"""
			actual_user = ConversationModel.objects(id=actual_user.id, chat_with=conversation_found).modify(
				chat_with=None, new=True, inc__chatted_times=-1)
			ConversationModel.objects(id=conversation_found.id, chat_with=actual_user).modify(
				chat_with=None, inc__chatted_times=-1)

			if not actual_user:
				# Se l'utente non viene modificato, vuol dire che, per qualche strana ragione è già stato abinato a qualcun'altro e non alla conversazione corrente.
				# Questo vuol dire che posso ritornare.
				return

			if count < 3:
				self.__engage_users(count=count + 1)
				return

			self._internal_send_text(self.current_conversation, self.translate('search_not_found'))

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
			for attachment in self.message_attachments:
				self._internal_send_attachment(self.current_conversation.chat_with, attachment)

		if self.message_text:
			self._internal_send_text(self.current_conversation.chat_with, self.message_text)
