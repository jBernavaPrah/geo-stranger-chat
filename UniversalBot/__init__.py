# coding=utf-8
from flask_babel import gettext, force_locale

import hashlib
import importlib

import logging

import datetime
import mimetypes
from urllib.parse import urlparse

from flask import url_for
from geopy import Nominatim
from mongoengine import Q

import config

from models import ConversationModel, ProxyUrlModel
from abc import ABC, abstractmethod


class Abstract(ABC):
	_service = None

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
	def get_caption_from_message(self, message):
		return ''

	@abstractmethod
	def get_data(self, message):
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
	def process(self, message):
		raise NotImplemented

	@abstractmethod
	def is_group(self, message):
		raise NotImplemented

	@abstractmethod
	def can_continue(self, message):
		raise NotImplemented


class Handler(Abstract):

	def __init__(self, message=None):
		self.current_conversation = None
		if message:
			if self.is_group(message):
				# TODO: Response with correct item?
				return

			self._get_conversation_from_message(message)

			self._

			self.process(message=message)



	@staticmethod
	def _registry_handler(user_model, handler_name):

		if hasattr(handler_name, '__name__'):
			handler_name = handler_name.__name__

		user_model.modify(next_function=handler_name, upsert=True)

	def _get_conversation_from_message(self, message):
		conversation_id = self.get_conversation_id_from_message(message)

		self.current_conversation = self._get_conversation(self.__class__.__name__, conversation_id, False)

	@staticmethod
	def _get_mimetype(url):
		# url = 'https://webchat.botframework.com/attachments/FSwuL5g77fPGefKmk280n9/0000025/0/RETRIBUZIONIRELATIVEALCORRENTEANNO.pdf?t=ddKbtD8p354.dAA.RgBTAHcAdQBMADUAZwA3ADcAZgBQAEcAZQBmAEsAbQBrADIAOAAwAG4AOQAtADAAMAAwADAAMAAyADUA.X982jTec0wE.7Iwg-WuAW5w.QUelqWJcqB280Dpd38Iw88xMK0dm2UBM-g-0b5aIaeM'
		p = urlparse(url)
		return mimetypes.guess_type(p.path)[0]

	@staticmethod
	def _(lang, text):
		with force_locale(lang):
			return gettext(text)

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

	def _check_response(self, message, check, strict=False):

		m = self.get_data(message)
		if not m:
			m = self.get_text_from_message(message)

		if not m:
			return False

		w = gettext(check)

		if not strict:
			return m.lower().strip() == w.lower().strip()

		return m == w

	@staticmethod
	def _get_sender(sender_class):
		mod = importlib.import_module(sender_class)
		return mod.CustomHandler()

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

	def _internal_send_text(self, user_model, text, format_with=None, keyboard=None):

		if format_with:
			text = text.format(**format_with)

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

	def not_compatible(self, message):
		with force_locale(self.current_conversation.language):
			self._internal_send_text(self.current_conversation, gettext(
				'I cannot understand that message sorry :(  It will not be sent to GeoStranger.'))

	def start_command(self, message):
		return self.welcome_command(message)

	def generic_command(self, message):

		logging.debug('Entering into Generic Command')
		# logging.debug('Message: \n\n%s' % json.dumps(message, indent=2, default=str))

		if not self.current_conversation:
			logging.debug('Not found user')
			self.welcome_command(message)
			return

		logging.debug('Found User %s ' % str(self.current_conversation.id))

		execute_command = self.get_text_from_message(message)
		# execute_command = execute_command.encode('utf-8')

		# logging.debug('Text with message: %s (len: %s)' % (str(execute_command), len(str(execute_command))))

		if execute_command and len(execute_command) and execute_command[0] == '/':

			logging.debug('Text (%s) is a command' % str(execute_command.encode('utf-8')))
			# logging.debug('Text (%s) is a command' % execute_command)

			command = execute_command[1:].strip()

			# annullo l'ultimo comando..
			next_f = self.current_conversation.next_function
			if next_f:
				logging.debug('Delete next_function of user (%s) ' % str(next_f))
				self.current_conversation.next_function = None
				self.current_conversation.save()

			logging.debug('Executing command')
			try:
				getattr(self, str(command) + '_command')(message)
				return
			except Exception as e:
				logging.debug('Command %s not found.' % (str(execute_command.encode('utf-8')) + '_command'))
				self.current_conversation.next_function = next_f
				self.current_conversation.save()

				# TODO: send message to user command not found!.
				with force_locale(self.current_conversation.language):
					self._internal_send_text(self.current_conversation, gettext(
						'I not have this command: %(command_text)s. To see all command send me /help.',
						command_text=execute_command))

				return

		logging.debug('User next_function: %s ' % str(self.current_conversation.next_function))
		if self.current_conversation.next_function:
			next_f = self.current_conversation.next_function
			self.current_conversation.next_function = None
			self.current_conversation.save()
			try:
				logging.debug('Executing function: %s ' % str(next_f))
				getattr(self, next_f)(message)
			except Exception as e:
				logging.exception(e)
				with force_locale(self.current_conversation.language):
					self._internal_send_text(self.current_conversation, gettext(
						'Internal error. Retry later..\n\n PS. I have reported this case to my creators.'))
				self._registry_handler(self.current_conversation, self.current_conversation.next_function)
			return

		if not self.current_conversation.chat_with:
			self.help_command(message)
			return

		""" Proxy the message to other user """

		self.__proxy_message(message)

	def welcome_command(self, message):

		if not self.current_conversation:
			conversation_id = self.get_conversation_id_from_message(message)
			language = self.get_user_language_from_message(message)

			self.current_conversation = ConversationModel(chat_type=str(self.__class__.__name__), conversation_id=str(conversation_id),
														  language=language)
			self.current_conversation.save()
			with force_locale(self.current_conversation.language):
				self._internal_send_text(self.current_conversation, gettext(
					'*Welcome GeoStranger!* \ud83d\ude00\ud83d\ude00!\n\nIf you continue and answare my questions, you accept the terms of my creators (%(terms_url)s).\nYou can delete all your information from my databases with command */delete*.\n\nFor the complete list of commands use */help*. \n\nTo send command simply click on button if present or send relative command with \"/\" in front. Example: \"/location\" ',
					terms_url=url_for('index.terms_page', _external=True)))

		if not self.current_conversation.location or not self.current_conversation.completed:
			self.location_command(message)
			return

		"""User is completed, need a search or change the location?"""
		with force_locale(self.current_conversation.language):
			self._internal_send_text(self.current_conversation,
									 gettext(
										 'To start new chat send me command /search.\n\nList of all commands /help.'))

	def location_command(self, message):

		with force_locale(self.current_conversation.language):
			self._internal_send_text(self.current_conversation, gettext(
				'To found best GeoStranger that match to you I need only one information, your current location. From where you write me?\n\n Enter the name of City and Region. *Nobody will know your real location.* GeoStranger will only see the name of your town/city.'),
									 keyboard=self.remove_keyboard())
		self._registry_handler(self.current_conversation, self._handler_location_step1)

	def delete_command(self, message):
		with force_locale(self.current_conversation.language):
			self._internal_send_text(self.current_conversation, gettext(
				'*Are you sure to delete all your data and stop talk with other GeoStrangers?*\n\nYou cannot undo anymore.'),
									 keyboard=self.new_keyboard(gettext('yes'),
																gettext('no')))
		self._registry_handler(self.current_conversation, self._handle_delete_step1)

	def terms_command(self, message):

		with force_locale(self.current_conversation.language):
			self._internal_send_text(self.current_conversation, gettext('Find our terms here: %(terms_url)s ',
																		terms_url=url_for('index.terms_page',
																						  _external=True)))

	def help_command(self, message):
		with force_locale(self.current_conversation.language):
			help_text = ''
			help_text += '/start ' + gettext(
				'Start new conversation with GeoStrangers or registry to our platform.') + "\n"
			help_text += '/new ' + gettext('Stop current chat and search for new Stranger.') + "\n"
			help_text += '/stop ' + gettext('Stop receiving GeoStrangers messages.') + "\n"
			help_text += '/delete ' + gettext('Delete your data from GeoStranger datacenters.') + "\n"
			help_text += '/terms ' + gettext('Show our Terms and Conditions.') + "\n"
			help_text += '/notification ' + gettext(
				'There are some information that my creators need to know? Or you found a Bug? Send to me.') + "\n"
			help_text += '/help ' + gettext('This help list.') + "\n"

			self._internal_send_text(self.current_conversation, gettext(
				'Hi GeoStranger! My work is to find new friend near you!\n\nOnce you have completed the initial phase you can search for a new GeoStranger by sending command */search*. If you send me */search* again, during the chat, I will look for you to find a new GeoStranger.\nTo not receive other GeoStranger send me the */stop* command. *List of command you can use with me:*\n\n%(help_text)s',
				help_text=help_text))

	def stop_command(self, message):

		if self.current_conversation.chat_with:
			with force_locale(self.current_conversation.language):
				self._internal_send_text(self.current_conversation, gettext(
					'Are you sure to stop receiving new GeoStranger?\n\nThis will stop also current chat.'),
										 keyboard=self.new_keyboard(gettext('yes'),
																	gettext('no')))
			self._registry_handler(self.current_conversation, self._handle_stop_step1)


		else:
			with force_locale(self.current_conversation.language):
				self._internal_send_text(self.current_conversation,
										 gettext('Are you sure to stop receiving new GeoStranger?'),
										 keyboard=self.new_keyboard(gettext('yes'),
																	gettext('no')))
			self._registry_handler(self.current_conversation, self._handle_stop_step1)

	def new_command(self, message):

		if not self.current_conversation.chat_with:
			self.search_command(message)
			return
		with force_locale(self.current_conversation.language):
			self._internal_send_text(self.current_conversation,
									 gettext('Sure to stop this chat and search new GeoStranger?'),
									 keyboard=self.new_keyboard(gettext('yes'),
																gettext('no')))
		self._registry_handler(self.current_conversation, self._handle_new_step1)

	def search_command(self, message):

		# La persona che ho parlato di recente deve avere una priorità più bassa di essere ripreso, ma non deve essere esculsa.
		# Una volta selezionata una persona, con la probabilità più alta, devo aggiornare il mio stato, sempre che non sia già stato preso.
		# *Non posso* semplicemente aggiornare il mio stato. Devo fare una query selettiva e aggiornare atomicamente il dato.

		# controlla se l'utente non è in coversazione, altrimenti esegui il command_stop.
		if self.current_conversation.chat_with:
			self.stop_command(message)
			return
		"""Per evitare di scrivere troppe volte in db"""
		with force_locale(self.current_conversation.language):
			self._internal_send_text(self.current_conversation, gettext('I have start searching..'))

		self.__engage_users()

	def _handle_new_step1(self, message):

		if not self._check_response(message, 'yes'):
			with force_locale(self.current_conversation.language):
				self._internal_send_text(self.current_conversation, gettext('Ok, not stopped.'))
			return

		if self.current_conversation.chat_with:
			# Devo disabilitare anche il search, in maniera tale che l'utente b clicchi su Search se vuole ancora cercare.
			# Questo mi permette di eliminare il problema webchat..
			# TODO: Fare in modo che solamente la webchat abbia questa richiesta. Altrimenti non disabilitare la possibilità di essere ricercati.
			# TODO: Trovare un modo alternativo.
			ConversationModel.objects(id=self.current_conversation.chat_with.id,
									  chat_with=self.current_conversation).modify(chat_with=None,
																				  allow_search=False)
			with force_locale(self.current_conversation.chat_with.language):
				self._internal_send_text(self.current_conversation.chat_with,
										 gettext('Geostranger disconnected.\n\nTo restart press /search'))

		# Se non è uguale a None, vuol dire che è stato scelto da qualcun altro.. e allora non devo mica cercarlo.
		_check_user = ConversationModel.objects(id=self.current_conversation.id,
												chat_with=self.current_conversation.chat_with).modify(
			chat_with=None, new=True)
		if not _check_user.chat_with:
			with force_locale(self.current_conversation.language):
				self._internal_send_text(self.current_conversation, gettext('I have start searching..'))
			self.__engage_users()

	def _handle_stop_step1(self, message):

		if not self._check_response(message, 'yes'):
			with force_locale(self.current_conversation.language):
				self._internal_send_text(self.current_conversation, gettext('Ok, not stopped.'))
			return

		if self.current_conversation.chat_with:
			# Devo disabilitare anche il search, in maniera tale che l'utente b clicchi su Search se vuole ancora cercare.
			# Questo mi permette di eliminare il problema webchat..
			# TODO: Fare in modo che solamente la webchat abbia questa richiesta. Altrimenti non disabilitare la possibilità di essere ricercati.
			# TODO: Trovare un modo alternativo.
			ConversationModel.objects(id=self.current_conversation.chat_with.id,
									  chat_with=self.current_conversation).modify(chat_with=None,
																				  allow_search=False)
			with force_locale(self.current_conversation.language):
				self._internal_send_text(self.current_conversation.chat_with,
										 gettext('Geostranger disconnected.\n\nTo restart press /search'))

		ConversationModel.objects(id=self.current_conversation.id,
								  chat_with=self.current_conversation.chat_with).modify(chat_with=None,
																						allow_search=False)
		with force_locale(self.current_conversation.language):
			self._internal_send_text(self.current_conversation, gettext('*Stopped*.\n\nTo restart press /search'))

	def _handle_delete_step1(self, message):

		if not self._check_response(message, 'yes'):
			with force_locale(self.current_conversation.language):
				self._internal_send_text(self.current_conversation, gettext("Good, *I haven't delete anythings*"))
			return

		self.current_conversation.deleted_at = datetime.datetime.utcnow()
		self.current_conversation.save()
		with force_locale(self.current_conversation.language):
			self._internal_send_text(self.current_conversation, gettext(
				'I have deleted all association of you in our data. Remember to delete also this chat.\n\n *Bye bye*. To restart, send me a message or use command /start.'))

	def _handler_location_step1(self, message):

		location_text = self.get_text_from_message(message)

		if not location_text:
			with force_locale(self.current_conversation.language):
				self._internal_send_text(self.current_conversation, gettext(
					'I cannot continue if you not send me your position. What is your current location?'),
										 keyboard=self.remove_keyboard())
			self._registry_handler(self.current_conversation, self._handler_location_step1)
			return

		geolocator = Nominatim()
		location = geolocator.geocode(location_text, language=self.current_conversation.language)

		if not location:
			""" Location non trovata.. """
			with force_locale(self.current_conversation.language):
				self._internal_send_text(self.current_conversation, gettext(
					"I haven't found %(location_text)s. Retry with other city or be more specific..",
					location_text=location_text))
			self._registry_handler(self.current_conversation, self._handler_location_step1)
			return

		""" Location trovata! Per il momento la salvo e chiedo se è corretta :) """
		self.current_conversation.location = [location.longitude, location.latitude]
		self.current_conversation.location_text = location.address
		self.current_conversation.save()

		with force_locale(self.current_conversation.language):
			yes_no_keyboard = self.new_keyboard(gettext('yes'), gettext('no'))
			self._internal_send_text(self.current_conversation,
									 gettext('Is correct this position?\n\n%(location_text)s',
											 location_text=location.address),
									 keyboard=yes_no_keyboard)
		self._registry_handler(self.current_conversation, self._handler_location_step2)

	def _handler_location_step2(self, message):

		if not self._check_response(message, 'yes'):
			""" Richiedo allora nuovamente la posizione """
			with force_locale(self.current_conversation.language):
				self._internal_send_text(self.current_conversation, gettext('Then, what is your current location?'),
										 keyboard=self.remove_keyboard())
			self._registry_handler(self.current_conversation, self._handler_location_step1)
			return

		with force_locale(self.current_conversation.language):
			self._internal_send_text(self.current_conversation, gettext(
				'Ok, I have saved *%(location_text)s* location.\n\nTo change it, use command /location.',
				location_text=self.current_conversation.location_text), )

		""" Location ok! """

		if not self.current_conversation.completed:
			self.current_conversation.completed = True
			self.current_conversation.save()
			with force_locale(self.current_conversation.language):
				self._internal_send_text(self.current_conversation, gettext(
					'Ok! :) We have finish. \n\n Now use /search to start talk and found new friends!'))

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
		user_found = ConversationModel.objects(Q(id__nin=exclude_users) & \
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

		logging.debug('Found %s user' % str(user_found))

		""" Se non ho trovato nessuno, devo solo aspettare che il sistema mi associ ad un altro geostranger. """
		if not user_found:
			""" Se non ho trovato nulla e non sono stato selezionato, aspetto.. succederà prima o poi :) """
			return

		actual_user = ConversationModel.objects(id=self.current_conversation.id,
												chat_with=None) \
			.modify(chat_with=user_found,
					last_engage_at=datetime.datetime.utcnow(),
					new=True)

		if not actual_user:
			""" Se sono già stato scelto durante questa query, allora semplicemente effettuo il release del utente.  """
			ConversationModel.objects(id=user_found.id, chat_with=actual_user).modify(chat_with=None)
			return

		"""Invia il messaggio al utente selezionato """
		with force_locale(user_found.language):

			if user_found.first_time_chat:
				send_text = gettext(
					'Super! I have found your GeoStranger, near *%(location_text)s*. Now, all message, video, image or audio will be sent directly to this GeoStranger in anonymously mode. (Use /stop to stop receiving new GeoStrangers)',
					location_text=actual_user.location_text)
			else:
				send_text = gettext(
					'New GeoStranger, near *%(location_text)s*. Start chat with it. (Use /stop to stop receiving new GeoStrangers)',
					location_text=actual_user.location_text)

		sent = self._internal_send_text(user_found, send_text)

		if not sent:
			""" il messaggio non è stato inviato.. probabilmente l'utente non è più disponibile, provvedo a togliere le associazioni"""
			ConversationModel.objects(id=actual_user.id, chat_with=user_found).modify(chat_with=None)
			ConversationModel.objects(id=user_found.id, chat_with=actual_user).modify(chat_with=None)

			# IS A WEBCHAT? Then disable it.
			# UserModel.objects(id=user_found.id, chat_type=str(webchat_bot.CustomHandler.Type)).modify(allow_search=False)

			return

		if user_found.first_time_chat:
			user_found.first_time_chat = False
			user_found.save()

		with force_locale(actual_user.language):
			if actual_user.first_time_chat:
				send_text = gettext(
					'Super! I have found your GeoStranger, near *%(location_text)s*. Now, all message, video, image or audio will be sent directly to this GeoStranger in anonymously mode. (Use /stop to stop receiving new GeoStrangers)',
					location_text=user_found.location_text)
			else:
				send_text = gettext(
					'New GeoStranger, near *%(location_text)s*. Start chat with it. (Use /stop to stop receiving new GeoStrangers)',
					location_text=user_found.location_text)

		self._internal_send_text(actual_user, send_text)

		if actual_user.first_time_chat:
			actual_user.first_time_chat = False
			actual_user.save()

	# LastChatsModel(from_user=actual_user, to_user=user_found).save()
	# LastChatsModel(from_user=user_found, to_user=actual_user).save()

	def __proxy_message(self, message):

		logging.debug('Proxy the message from ConversationModel(%s) to ConversationModel(%s)' % (
			self.current_conversation.id, self.current_conversation.chat_with.id))

		# TODO: If conversation return false, then need to stop it!

		self.current_conversation.update(inc__messages_sent=1)
		self.current_conversation.chat_with.update(inc__messages_received=1)

		text_message = self.get_text_from_message(message)

		if text_message:
			self._internal_send_text(self.current_conversation.chat_with, text_message)

		attachments_url = self.get_attachments_url_from_message(message)
		if len(attachments_url):
			for attachment_url in attachments_url:
				self._internal_send_attachment(self.current_conversation.chat_with, attachment_url)

		caption_message = self.get_caption_from_message(message)
		if caption_message:
			self._internal_send_text(self.current_conversation.chat_with, caption_message)
