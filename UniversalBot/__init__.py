# coding=utf-8
import hashlib
import importlib
import json
import logging

import datetime

from flask import url_for
from geopy import Nominatim
from mongoengine import Q

import config
from UniversalBot.languages import trans_message
from models import UserModel
import abc

from utilities import jwt


class Helper(object):
	__metaclass__ = abc.ABCMeta
	Type = None

	@staticmethod
	def _registry_handler(user_model, handler_name):

		if hasattr(handler_name, '__name__'):
			handler_name = handler_name.__name__

		user_model.modify(next_function=handler_name, upsert=True)

	def _get_user_from_message(self, message):
		user_id = self.get_user_id_from_message(message)

		return self._get_user(self.Type, user_id, False)

	@staticmethod
	def _md5(_str):

		return hashlib.md5((config.SECRET_KEY + _str).encode()).hexdigest()

	def _get_user(self, chat_type, user_id, strict=True):

		user = UserModel.objects(Q(chat_type=str(chat_type)) & \
								 Q(user_id=str(user_id)) & \
								 Q(deleted_at=None)) \
			.first()

		if not user and strict:
			logging.exception('User required, but not found.')
			raise RuntimeError

		return user

	def _check_response(self, message, check, strict=False):

		language = self.get_user_language_from_message(message)
		m = self.get_data(message)
		if not m:
			m = self.get_text_from_message(message)

		if not m:
			return False

		w = trans_message(language, check)

		if not strict:
			return m.lower().strip() == w.lower().strip()

		return m == w

	@staticmethod
	def _get_sender(sender_class):
		mod = importlib.import_module(sender_class)
		return mod.CustomHandler()

	@abc.abstractmethod
	def get_user_id_from_message(self, message):
		return 0

	@abc.abstractmethod
	def get_user_language_from_message(self, message):
		return ''

	@abc.abstractmethod
	def get_images_url_from_message(self, message):
		return []

	@abc.abstractmethod
	def get_videos_url_from_message(self, message):
		return []

	@abc.abstractmethod
	def get_documents_url_from_message(self, message):
		return []

	@abc.abstractmethod
	def get_audios_url_from_message(self, message):
		return []

	@abc.abstractmethod
	def get_text_from_message(self, message):
		return ''

	@abc.abstractmethod
	def get_caption_from_message(self, message):
		return ''

	@abc.abstractmethod
	def get_data(self, message):
		return ''

	@staticmethod
	def _secure_download(file_url):
		token = jwt.dumps(str(file_url))
		return url_for('index.download_file', token=token, _external=True)

	@staticmethod
	def _url_play_audio(file_url):
		token = jwt.dumps(str(file_url))
		return url_for('index.play_audio', token=token, _external=True)

	@staticmethod
	def _url_play_video(file_url):
		token = jwt.dumps(file_url)
		return url_for('index.play_video', token=token, _external=True)


class Handler(Helper):
	Type = None
	_service = None

	def __init__(self, config=False):

		logging.info('Starting %s' % str(self.Type))

		if config:
			self.registry_commands()
			logging.info('Registering command %s Completed.' % str(self.Type))
			self.configuration()
			logging.info('Configuration command %s Completed.' % str(self.Type))

		logging.info('Starting %s Completed.' % str(self.Type))

	@abc.abstractmethod
	def configuration(self):
		pass

	@abc.abstractmethod
	def new_keyboard(self, *args):
		return []

	def _select_keyboard(self, user_model):

		# TODO: need to bee only see in some situations. Not always.

		commands = ['/terms', '/help', '/delete']

		if user_model.location:
			commands = ['/search', '/location', '/terms', '/help', '/delete']

		# todo: not show search if user is into searching...

		if user_model.chat_with:
			commands = ['/new', '/stop']

		return self.new_keyboard(*commands)

	@abc.abstractmethod
	def remove_keyboard(self):
		pass

	@abc.abstractmethod
	def real_send_text(self, user_model, text, keyboard=None):
		raise NotImplemented

	@abc.abstractmethod
	def real_send_photo(self, user_model, file_url, keyboard=None):
		raise NotImplemented

	@abc.abstractmethod
	def real_send_video(self, user_model, file_url, keyboard=None):
		raise NotImplemented

	@abc.abstractmethod
	def real_send_audio(self, user_model, file_url, keyboard=None):
		raise NotImplemented

	@abc.abstractmethod
	def real_send_document(self, user_model, file_url, keyboard=None):
		raise NotImplemented

	def send_audio(self, user_model, file_url, keyboard=None):

		sender = self
		if self.Type != user_model.chat_type:
			sender = self._get_sender(user_model.chat_type)

		if not keyboard:
			keyboard = sender._select_keyboard(user_model)

		try:
			sender.real_send_audio(user_model, file_url, keyboard=keyboard)
			return True
		except Exception as e:
			return False

	def send_video(self, user_model, file_url, keyboard=None):
		sender = self
		if self.Type != user_model.chat_type:
			sender = self._get_sender(user_model.chat_type)

		if not keyboard:
			keyboard = sender._select_keyboard(user_model)

		try:
			sender.real_send_video(user_model, file_url, keyboard=keyboard)
			return True
		except Exception as e:
			return False

	def send_photo(self, user_model, file_url, keyboard=None):

		sender = self
		if self.Type != user_model.chat_type:
			sender = self._get_sender(user_model.chat_type)

		if not keyboard:
			keyboard = sender._select_keyboard(user_model)

		try:
			sender.real_send_photo(user_model, file_url, keyboard=keyboard)
			return True
		except Exception as e:
			return False

	def send_document(self, user_model, file_url, keyboard=None):
		sender = self
		if self.Type != user_model.chat_type:
			sender = self._get_sender(user_model.chat_type)

		if not keyboard:
			keyboard = sender._select_keyboard(user_model)

		try:
			sender.real_send_document(user_model, file_url, keyboard=keyboard)
			return True
		except Exception as e:
			return False

	def send_text(self, user_model, text, format_with=None, keyboard=None):

		# if language:
		text = trans_message(user_model.language, text)

		if format_with:
			text = text.format(**format_with)

		sender = self
		if self.Type != user_model.chat_type:
			sender = self._get_sender(user_model.chat_type)

		if not keyboard:
			keyboard = sender._select_keyboard(user_model)

		try:
			sender.real_send_text(user_model, text, keyboard=keyboard)
			return True
		except Exception as e:
			return False

	@abc.abstractmethod
	def registry_commands(self):
		pass

	def not_compatible(self, message):
		user = self._get_user_from_message(message)
		self.send_text(user, 'not_compatible')

	def start_command(self, message):
		return self.welcome_command(message)

	def generic_command(self, message):

		logging.debug('Entering into Generic Command')
		# logging.debug('Message: \n\n%s' % json.dumps(message, indent=2, default=str))

		user = self._get_user_from_message(message)

		if not user:
			logging.debug('Not found user')
			self.welcome_command(message)
			return

		logging.debug('Found User %s ' % str(user.id))

		execute_command = self.get_text_from_message(message)
		# execute_command = execute_command.encode('utf-8')

		# logging.debug('Text with message: %s (len: %s)' % (str(execute_command), len(str(execute_command))))

		if execute_command and len(execute_command) and execute_command[0] == '/':

			logging.debug('Text (%s) is a command' % str(execute_command.encode('utf-8')))
			# logging.debug('Text (%s) is a command' % execute_command)

			command = execute_command[1:].strip()

			# annullo l'ultimo comando..
			next_f = user.next_function
			if next_f:
				logging.debug('Delete next_function of user (%s) ' % str(next_f))
				user.next_function = None
				user.save()

			logging.debug('Executing command')
			try:
				getattr(self, str(command) + '_command')(message)
				return
			except Exception as e:
				logging.debug('Command %s not found.' % (str(execute_command.encode('utf-8'))+ '_command'))
				user.next_function = next_f
				user.save()

				# TODO: send message to user command not found!.

				return

		logging.debug('User next_function: %s ' % str(user.next_function))
		if user.next_function:
			next_f = user.next_function
			user.next_function = None
			user.save()
			try:
				logging.debug('Executing function: %s ' % str(next_f))
				getattr(self, next_f)(message)
			except Exception as e:
				logging.exception(e)
				self.send_text(user, 'error')
				self._registry_handler(user, user.next_function)
			return

		if not user.chat_with:
			# self.send_text(user_id, 'conversation_stopped_by_other_geostranger', language=language)
			return

		""" Proxy the message to other user """

		self.__proxy_message(message, user, user.chat_with)

	def welcome_command(self, message):

		user = self._get_user_from_message(message)

		if not user:
			user_id = self.get_user_id_from_message(message)
			language = self.get_user_language_from_message(message)

			user = UserModel(chat_type=str(self.Type), user_id=str(user_id), language=language)
			user.save()
			self.send_text(user, 'welcome')

		if not user.location or not user.completed:
			self.location_command(message)
			return

		"""User is completed, need a search or change the location?"""
		self.send_text(user, 'search')

	def location_command(self, message):

		user = self._get_user_from_message(message)

		self.send_text(user, 'ask_location', keyboard=self.remove_keyboard())
		self._registry_handler(user, self._handler_location_step1)

	def delete_command(self, message):
		user = self._get_user_from_message(message)

		self.send_text(user, 'ask_delete_sure',
					   keyboard=self.new_keyboard(trans_message(user.language, 'yes'),
												  trans_message(user.language, 'no')))
		self._registry_handler(user, self._handle_delete_step1)

	def terms_command(self, message):
		user = self._get_user_from_message(message)
		self.send_text(user, 'terms')

	def help_command(self, message):
		user = self._get_user_from_message(message)

		help_text = ''
		help_text += trans_message(user.language, 'command_start') + "\n"
		help_text += trans_message(user.language, 'command_stop') + "\n"
		help_text += trans_message(user.language, 'command_delete') + "\n"
		help_text += trans_message(user.language, 'command_terms') + "\n"
		help_text += trans_message(user.language, 'command_notify') + "\n"
		help_text += trans_message(user.language, 'command_help') + "\n"

		self.send_text(user, 'help', format_with={'help_text': help_text})

	def stop_command(self, message):

		user = self._get_user_from_message(message)

		if user.chat_with:

			self.send_text(user, 'ask_stop_also_current_chat',
						   keyboard=self.new_keyboard(trans_message(user.language, 'yes'),
													  trans_message(user.language, 'no')))
			self._registry_handler(user, self._handle_stop_step1)


		else:
			self.send_text(user, 'ask_stop_sure',
						   keyboard=self.new_keyboard(trans_message(user.language, 'yes'),
													  trans_message(user.language, 'no')))
			self._registry_handler(user, self._handle_stop_step1)

	def new_command(self, message):

		user = self._get_user_from_message(message)

		self.send_text(user, 'search_new',
					   keyboard=self.new_keyboard(trans_message(user.language, 'yes'),
												  trans_message(user.language, 'no')))
		self._registry_handler(user, self._handle_new_step1)

	def search_command(self, message):

		# La persona che ho parlato di recente deve avere una priorità più bassa di essere ripreso, ma non deve essere esculsa.
		# Una volta selezionata una persona, con la probabilità più alta, devo aggiornare il mio stato, sempre che non sia già stato preso.
		# *Non posso* semplicemente aggiornare il mio stato. Devo fare una query selettiva e aggiornare atomicamente il dato.

		actual_user = self._get_user_from_message(message)

		# controlla se l'utente non è in coversazione, altrimenti esegui il command_stop.
		if actual_user.chat_with:
			self.stop_command(message)
			return
		"""Per evitare di scrivere troppe volte in db"""

		if not actual_user.allow_search:
			actual_user.allow_search = True
			actual_user.save()

		self.send_text(actual_user, 'in_search')

		self.__engage_users(actual_user)

	def _handle_new_step1(self, message):
		user = self._get_user_from_message(message)

		if not self._check_response(message, 'yes'):
			# TODO: edita il messaggio!
			self.send_text(user, 'not_stopped')
			return

		if user.chat_with:
			self.send_text(user.chat_with, 'conversation_stopped_by_other_geostranger')
			""" Atomically! :D """
			UserModel.objects(id=user.chat_with.id, chat_with=user).modify(chat_with=None)

		UserModel.objects(id=user.id, chat_with=user.chat_with).modify(chat_with=None, allow_search=False)

		self.__engage_users(user)

	def _handle_stop_step1(self, message):
		user = self._get_user_from_message(message)

		if not self._check_response(message, 'yes'):
			# TODO: edita il messaggio!
			self.send_text(user, 'not_stopped')
			return

		if user.chat_with:
			self.send_text(user.chat_with, 'conversation_stopped_by_other_geostranger')
			""" Atomically! :D """
			UserModel.objects(id=user.chat_with.id, chat_with=user).modify(chat_with=None)

		UserModel.objects(id=user.id, chat_with=user.chat_with).modify(chat_with=None, allow_search=False)

		# TODO: edita il messaggio!
		self.send_text(user, 'stop')

	def _handle_delete_step1(self, message):

		user = self._get_user_from_message(message)

		if not self._check_response(message, 'yes'):
			self.send_text(user, 'not_deleted')
			return

		user.deleted_at = datetime.datetime.utcnow()
		user.save()
		self.send_text(user, 'delete_completed')

	def _handler_location_step1(self, message):

		user = self._get_user_from_message(message)
		location_text = self.get_text_from_message(message)

		if not location_text:
			self.send_text(user, 'location_error', keyboard=self.remove_keyboard())
			self._registry_handler(user, self._handler_location_step1)
			return

		geolocator = Nominatim()
		location = geolocator.geocode(location_text, language=user.language)

		if not location:
			""" Location non trovata.. """
			self.send_text(user, 'location_not_found', format_with={'location_text': location_text})
			self._registry_handler(user, self._handler_location_step1)
			return

		""" Location trovata! Per il momento la salvo e chiedo se è corretta :) """
		user.location = [location.longitude, location.latitude]
		user.location_text = location.address
		user.save()

		yes_no_keyboard = self.new_keyboard(trans_message(user.language, 'yes'), trans_message(user.language, 'no'))

		# TODO: qua posso modificare il testo, non inviarlo uno nuovo..

		self.send_text(user, 'ask_location_is_correct', format_with={'location_text': location.address},
					   keyboard=yes_no_keyboard)
		self._registry_handler(user, self._handler_location_step2)

	def _handler_location_step2(self, message):

		user = self._get_user_from_message(message)

		if not self._check_response(message, 'yes'):
			""" Richiedo allora nuovamente la posizione """
			self.send_text(user, 're_ask_location', keyboard=self.remove_keyboard())
			self._registry_handler(user, self._handler_location_step1)
			return

		self.send_text(user, 'location_saved', format_with={'location_text': user.location_text})

		""" Location ok! """

		if not user.completed:
			user.completed = True
			user.save()
			self.send_text(user, 'completed')

	def __engage_users(self, actual_user):
		# L'utente fa il search. Posso utilizzarlo solamente se l'utente non è al momento sotto altra conversation.
		# Questo vuol dire che non devo fare nessun ciclo. E' UNA FUNZIONE ONE SHOT!
		# E se non trovo nulla, devo aspettare che sia un altro a fare questa operazione e "Trovarmi"..
		#

		# TODO: Viene selezionato sempre lo stesso utente per due utenti nello stesso posto. Invece di effettuare il giro.
		# http://docs.mongoengine.org/guide/querying.html#further-aggregation

		user_found = UserModel.objects(Q(id__ne=actual_user.id) & \
									   Q(chat_with=None) & \
									   Q(allow_search=True) & \
									   Q(completed=True) & \
									   Q(location__near=actual_user.location)) \
			.order_by("+updated_at") \
			.modify(chat_with=actual_user, new=True)

		logging.debug('Found %s user' % str(user_found))

		""" Se non ho trovato nessuno, devo solo aspettare che il sistema mi associ ad un altro geostranger. """
		if not user_found:
			""" Se non ho trovato nulla e non sono stato selezionato, aspetto.. succederà prima o poi :) """
			return

		"""Effettuo il reload per caricare l'ultima versione del modello"""
		""" Devo effettuare atomicamente qua!! """

		actual_user = UserModel.objects(id=actual_user.id, chat_with=None).modify(chat_with=user_found, new=True)

		if actual_user.chat_with.id != user_found.id:
			""" Se sono già stato scelto durante questa query, allora semplicemente effettuo il release del utente.  """
			UserModel.objects(id=user_found.id, chat_with=actual_user).modify(chat_with=None)
			return

		"""Invia il messaggio al utente selezionato """

		uf_tx = 'found_new_geostranger_first_time' if user_found.first_time_chat else 'found_new_geostranger'

		sent = self.send_text(user_found, uf_tx, format_with={'location_text': actual_user.location_text})

		if not sent:
			""" il messaggio non è stato inviato.. probabilmente l'utente non è più disponibile, provvedo a togliere le associazioni"""
			UserModel.objects(id=actual_user.id, chat_with=user_found).modify(chat_with=None)
			UserModel.objects(id=user_found.id, chat_with=actual_user).modify(chat_with=None)
			return

		if user_found.first_time_chat:
			user_found.first_time_chat = False
			user_found.save()

		au_tx = 'found_new_geostranger_first_time' if actual_user.first_time_chat else 'found_new_geostranger'

		self.send_text(actual_user, au_tx, format_with={'location_text': user_found.location_text})

		if actual_user.first_time_chat:
			actual_user.first_time_chat = False
			actual_user.save()

	def __proxy_message(self, message, from_user_model, to_user_model):

		logging.debug('Proxy the message from UserModel(%s) to UserModel(%s)' % (from_user_model.id, to_user_model.id))

		text_message = self.get_text_from_message(message)

		if text_message:
			self.send_text(to_user_model, text_message)

		images_url = self.get_images_url_from_message(message)
		if len(images_url):
			for image_url in images_url:
				self.send_photo(to_user_model, image_url)

		videos_url = self.get_videos_url_from_message(message)
		if len(videos_url):
			for video_url in videos_url:
				self.send_video(to_user_model, video_url)

		documents_url = self.get_documents_url_from_message(message)
		if len(documents_url):
			for document_url in documents_url:
				self.send_document(to_user_model, document_url)

		audios_url = self.get_audios_url_from_message(message)
		if len(audios_url):
			for audio_url in audios_url:
				self.send_audio(to_user_model, audio_url)

		caption_message = self.get_caption_from_message(message)
		if caption_message:
			self.send_text(to_user_model, caption_message)

	@abc.abstractmethod
	def process(self, request):
		raise NotImplemented
