# coding=utf-8
import datetime
import hashlib
import importlib
import logging
import mimetypes
from abc import ABC, abstractmethod
from urllib.parse import urlparse

from flask import url_for
from flask_babel import gettext, force_locale
from geopy import Nominatim
from mongoengine import Q

import config
from UniversalBot.languages import lang
from models import ConversationModel, ProxyUrlModel


class Abstract(ABC):
	_service = None

	@abstractmethod
	def need_expire(self, message):
		return False

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


class Handler(Abstract):

	def __init__(self, request=None):
		self.current_conversation = None
		self.message_text = ''
		self.message_attachments = []

		self._actual_message = None

		if request:

			messages = self.extract_message(request)

			if isinstance(messages, (list, tuple)):
				for message in messages:
					self._process_message(message)

			else:
				self._process_message(messages)

	def _process_message(self, message):

		self._actual_message = message

		self._get_conversation_from_message(message)

		if self.need_expire(message):
			self._refresh_expire()

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

		self.generic_command()

	def _is_user_allowed(self):
		return True

	def _refresh_expire(self):
		self.current_conversation.expire_at = datetime.datetime.utcnow()
		self.current_conversation.save()

	@staticmethod
	def _registry_handler(user_model, handler_name):

		if hasattr(handler_name, '__name__'):
			handler_name = handler_name.__name__

		user_model.modify(next_function=handler_name, upsert=True)

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

		# TODO: do a head to url if no mimetypes givven by extension!

		# url = 'https://webchat.botframework.com/attachments/FSwuL5g77fPGefKmk280n9/0000025/0/RETRIBUZIONIRELATIVEALCORRENTEANNO.pdf?t=ddKbtD8p354.dAA.RgBTAHcAdQBMADUAZwA3ADcAZgBQAEcAZQBmAEsAbQBrADIAOAAwAG4AOQAtADAAMAAwADAAMAAyADUA.X982jTec0wE.7Iwg-WuAW5w.QUelqWJcqB280Dpd38Iw88xMK0dm2UBM-g-0b5aIaeM'
		p = urlparse(url)
		return mimetypes.guess_type(p.path)[0]

	def translate(self, text, **variables):

		text = lang.bot_messsages.get(text, text)

		if self.current_conversation and self.current_conversation.language:
			with force_locale(self.current_conversation.language):
				return gettext(text, **variables)

		return gettext(text, **variables)

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
	def _get_sender(sender_class):
		mod = importlib.import_module('UniversalBot')
		return getattr(mod, sender_class)()

	@staticmethod
	def _secure_download(file_url):
		proxy = ProxyUrlModel(url=file_url).save()
		return url_for('index.download_action', _id=proxy.id, _external=True)

	@staticmethod
	def _url_play_audio(file_url):
		proxy = ProxyUrlModel(url=file_url).save()
		return url_for('index.audio_page', _id=proxy.id, _external=True)

	@staticmethod
	def _url_play_video(file_url):
		proxy = ProxyUrlModel(url=file_url).save()
		return url_for('index.video_page', _id=proxy.id, _external=True)

	def _select_keyboard(self, user_model):

		# TODO: need to bee only see in some situations. Not always.

		commands = ['/terms', '/help', '/delete']

		if user_model.location:
			commands = ['/search', '/location', '/terms', '/help', '/delete']

		# todo: not show search if user is into searching...

		if user_model.chat_with:
			commands = ['/new', '/stop']

		return self.new_keyboard(*commands)

	def _internal_send_attachment(self, user_model, file_url, keyboard=None):
		sender = self
		if self.__class__.__name__ != user_model.chat_type:
			sender = self._get_sender(user_model.chat_type)

		if not keyboard:
			keyboard = sender._select_keyboard(user_model)

		# TODO: Secure url
		content_type = self._get_mimetype(file_url)
		secure_url = self._secure_download(file_url)

		try:
			sender.bot_send_attachment(user_model, secure_url, content_type, keyboard=keyboard)
			return True
		except Exception as e:
			return False

	def _internal_send_text(self, user_model, text, keyboard=None):

		sender = self
		if self.__class__.__name__ != user_model.chat_type:
			sender = self._get_sender(user_model.chat_type)

		if not keyboard:
			keyboard = sender._select_keyboard(user_model)

		try:
			sender.bot_send_text(user_model, text, keyboard=keyboard)
			return True
		except Exception as e:
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

		if self.message_text and len(self.message_text) and self.message_text[0] == '/':

			logging.debug('Text (%s) is a command' % str(self.message_text.encode('utf-8')))
			# logging.debug('Text (%s) is a command' % execute_command)

			command = self.message_text[1:].strip()

			# annullo l'ultimo comando..
			next_f = self.current_conversation.next_function
			if next_f:
				logging.debug('Delete next_function of user (%s) ' % str(next_f))
				self.current_conversation.next_function = None
				self.current_conversation.save()

			logging.debug('Executing command')
			try:
				getattr(self, str(command) + '_command')()
				return
			except Exception as e:
				logging.exception(e)
				self.current_conversation.next_function = next_f
				self.current_conversation.save()

				self._internal_send_text(self.current_conversation,
										 self.translate('error'))

				return

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

		if self.current_conversation.chat_with:
			self.__proxy_message()
			return

		if not self.current_conversation.completed:
			logging.debug('Conversation not completed')
			self.welcome_command()
			return

		""" Proxy the message to other user """

		self.help_command()

	def welcome_command(self):

		self._internal_send_text(self.current_conversation,
								 self.translate('welcome', terms_url=url_for('index.terms_page', _external=True)))

		if not self.current_conversation.location or not self.current_conversation.completed:
			self.location_command()
			return

		"""User is completed, need a search or change the location?"""
		self._internal_send_text(self.current_conversation, self.translate('search'))

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
								 self.translate('terms', terms_url=url_for('index.terms_page', _external=True)))

	def help_command(self):
		self._internal_send_text(self.current_conversation, self.translate('help'))

	def stop_command(self):

		if self.current_conversation.chat_with:
			self._internal_send_text(self.current_conversation, self.translate('ask_stop_also_current_chat'),
									 keyboard=self.new_keyboard(self.translate('yes'),
																self.translate('no')))
			self._registry_handler(self.current_conversation, self._handle_stop_step1)


		else:
			self._internal_send_text(self.current_conversation,
									 self.translate('ask_stop_sure'),
									 keyboard=self.new_keyboard(self.translate('yes'),
																self.translate('no')))
			self._registry_handler(self.current_conversation, self._handle_stop_step1)

	def new_command(self):

		if not self.current_conversation.chat_with:
			self.search_command()
			return
		self._internal_send_text(self.current_conversation,
								 self.translate('sure_search_new'),
								 keyboard=self.new_keyboard(self.translate('yes'),
															self.translate('no')))
		self._registry_handler(self.current_conversation, self._handle_new_step1)

	def search_command(self):

		# La persona che ho parlato di recente deve avere una priorità più bassa di essere ripreso, ma non deve essere esculsa.
		# Una volta selezionata una persona, con la probabilità più alta, devo aggiornare il mio stato, sempre che non sia già stato preso.
		# *Non posso* semplicemente aggiornare il mio stato. Devo fare una query selettiva e aggiornare atomicamente il dato.

		# controlla se l'utente non è in coversazione, altrimenti esegui il command_stop.
		if self.current_conversation.chat_with:
			self.stop_command()
			return
		"""Per evitare di scrivere troppe volte in db"""
		self._internal_send_text(self.current_conversation, self.translate('in_search'))

		self.__engage_users()

	def _handle_new_step1(self):

		if not self._check_response('yes'):
			self._internal_send_text(self.current_conversation, self.translate('not_stopped'))
			return

		if self.current_conversation.chat_with:
			# Devo disabilitare anche il search, in maniera tale che l'utente b clicchi su Search se vuole ancora cercare.
			# Questo mi permette di eliminare il problema webchat..
			# TODO: Fare in modo che solamente la webchat abbia questa richiesta. Altrimenti non disabilitare la possibilità di essere ricercati.
			# TODO: Trovare un modo alternativo.
			ConversationModel.objects(id=self.current_conversation.chat_with.id,
									  chat_with=self.current_conversation).modify(chat_with=None,
																				  allow_search=False)

			self._internal_send_text(self.current_conversation.chat_with,
									 self.translate('conversation_stopped_by_other_geostranger'))

		# Se non è uguale a None, vuol dire che è stato scelto da qualcun altro.. e allora non devo mica cercarlo.
		_check_user = ConversationModel.objects(id=self.current_conversation.id,
												chat_with=self.current_conversation.chat_with).modify(
			chat_with=None, new=True)
		if not _check_user.chat_with:
			self._internal_send_text(self.current_conversation, self.translate('in_search'))
			self.__engage_users()

	def _handle_stop_step1(self):

		if not self._check_response('yes'):
			self._internal_send_text(self.current_conversation, self.translate('not_stopped'))
			return

		if self.current_conversation.chat_with:
			# Devo disabilitare anche il search, in maniera tale che l'utente b clicchi su Search se vuole ancora cercare.
			# Questo mi permette di eliminare il problema webchat..
			# TODO: Fare in modo che solamente la webchat abbia questa richiesta. Altrimenti non disabilitare la possibilità di essere ricercati.
			# TODO: Trovare un modo alternativo.
			ConversationModel.objects(id=self.current_conversation.chat_with.id,
									  chat_with=self.current_conversation).modify(chat_with=None,
																				  allow_search=False)
			self._internal_send_text(self.current_conversation.chat_with,
									 self.translate('conversation_stopped_by_other_geostranger'))

		ConversationModel.objects(id=self.current_conversation.id,
								  chat_with=self.current_conversation.chat_with).modify(chat_with=None,
																						allow_search=False)
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
																			   location_text=self.message_text))
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
																		   location_text=self.current_conversation.location_text), )

		""" Location ok! """

		if not self.current_conversation.completed:
			self.current_conversation.completed = True
			self.current_conversation.save()
			self._internal_send_text(self.current_conversation, self.translate('completed'))

	def __engage_users(self):

		if not self.current_conversation.allow_search:
			self.current_conversation.allow_search = True
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
													   Q(allow_search=True) & \
													   Q(completed=True) & \
													   Q(location__near=self.current_conversation.location)) \
			.order_by("+created_at") \
			.order_by("+messages_sent") \
			.order_by("+messages_received") \
			.order_by("+last_engage_at") \
			.modify(chat_with=self.current_conversation,
					last_engage_at=datetime.datetime.utcnow(),
					new=True)

		""" Memurandum: Il più vuol dire crescendo (0,1,2,3) il meno vuol dire decrescendo (3,2,1,0) """
		""" Memurandum: Prima ordino per quelli meno importanti, poi per quelli più importanti """

		logging.debug('Found %s user' % str(conversation_found))

		""" Se non ho trovato nessuno, devo solo aspettare che il sistema mi associ ad un altro geostranger. """
		if not conversation_found:
			""" Se non ho trovato nulla e non sono stato selezionato, aspetto.. succederà prima o poi :) """
			return

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
			ConversationModel.objects(id=actual_user.id, chat_with=conversation_found).modify(chat_with=None)
			ConversationModel.objects(id=conversation_found.id, chat_with=actual_user).modify(chat_with=None)

			# IS A WEBCHAT? Then disable it.
			# UserModel.objects(id=user_found.id, chat_type=str(webchat_bot.CustomHandler.Type)).modify(allow_search=False)

			return

		if conversation_found.first_time_chat:
			conversation_found.first_time_chat = False
			conversation_found.save()

		if actual_user.first_time_chat:
			send_text = 'found_new_geostranger_first_time'
		else:
			send_text = 'found_new_geostranger'

		self._internal_send_text(actual_user, self.translate(send_text, location_text=conversation_found.location_text))

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
