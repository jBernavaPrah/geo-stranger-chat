# coding=utf-8
import importlib
import logging

import datetime
import urlparse

import os
import requests
from flask import url_for
from geopy import Nominatim
from mongoengine import Q

from languages import trans_message
from models import UserModel, MessageModel, FileModel
import abc

from utilities import jwt


class Helper(object):
	__metaclass__ = abc.ABCMeta
	Type = None

	@staticmethod
	def _registry_handler(user_model, handler_name):
		""" Salvo un handler per l'utente. Potrò gestire le risposte direttamente nel software.
			message_id: mi serve per poter modificare il messaggio e non inviare uno nuovo ogni volta.
		"""
		if hasattr(handler_name, '__name__'):
			handler_name = handler_name.__name__

		UserModel.objects(chat_type=str(user_model.chat_type), user_id=str(user_model.user_id), deleted_at=None) \
			.modify(next_function=handler_name, upsert=True)

	def _get_user_from_message(self, message):
		user_id = self.get_user_id_from_message(message)
		return self._get_user(self.Type, user_id, False)

	@staticmethod
	def _get_user(chat_type, user_id, strict=True):

		user = UserModel.objects(Q(chat_type=str(chat_type)) & \
								 Q(user_id=str(user_id)) & \
								 Q(deleted_at=None)) \
			.first()

		if not user and strict:
			logging.exception('User required, but not found.')
			raise RuntimeError

		return user

	def _decode_unicode(self, text):
		try:
			return unicode(text, 'utf-8')
		except TypeError:
			return text

	def _check_response(self, message, check, strict=False):

		language = self.get_user_language_from_message(message)
		m = self.get_data(message)
		if not m:
			m = self.get_text_from_message(message)

		if not m:
			return False

		w = trans_message(language, check)

		if not strict:
			return self._decode_unicode(m.lower().strip()) == self._decode_unicode(w.lower().strip())

		return self._decode_unicode(m) == self._decode_unicode(w)

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
	def get_image_url_from_message(self, message):
		return None

	@abc.abstractmethod
	def get_video_url_from_message(self, message):
		return None

	@abc.abstractmethod
	def get_document_url_from_message(self, message):
		return None

	@abc.abstractmethod
	def get_audio_url_from_message(self, message):
		return None

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
	def _download_url_to_file_model(url, _f, content_type):
		with requests.get(url, stream=True) as r:

			if r.status_code != 200:
				msg = 'The server returned HTTP {0} {1}. Response body:\n[{2}]' \
					.format(r.status_code, r.reason, r.text)

				logging.warn(msg)
				return

			try:
				a = urlparse.urlparse(url)
				filename = os.path.basename(a.path)
			except Exception:
				filename = ''

			ct = r.headers.get('content-type', content_type)
			_f.new_file(content_type=ct, filename=filename)

			for chunk in r.iter_content(255):
				_f.write(chunk)
			_f.close()
		return

	@staticmethod
	def _url_download_document(file_model):
		token = jwt.dumps(str(file_model.id))
		return url_for('index.download_file', token=token, _external=True)

	@staticmethod
	def _url_play_audio(file_model):
		token = jwt.dumps(str(file_model.id))
		return url_for('index.play_audio', token=token, _external=True)

	@staticmethod
	def _url_play_video(file_model):
		token = jwt.dumps(file_model.id)
		return url_for('index.play_video', token=token, _external=True)

	def _save_file(self, file_url, content_type):
		_f = FileModel.objects(chat_type=self.Type, file_id=file_url).first()
		if _f:
			return _f

		_f = FileModel(chat_type=self.Type, file_id=file_url)

		self._download_url_to_file_model(file_url, _f.file, content_type)

		_f.save()
		return _f


class Handler(Helper):
	Type = None
	_service = None

	def __init__(self, config=False):
		if config:
			self.registry_commands()
			self.configuration()

	@abc.abstractmethod
	def configuration(self):
		pass

	@abc.abstractmethod
	def new_keyboard(self, *args):
		pass

	def _select_keyboard(self, user_model):

		commands = ['/terms', '/help', '/delete']

		if user_model.location:
			commands = ['/search', '/location', '/terms', '/help', '/delete']

		if user_model.chat_with:
			commands = ['/search', '/stop']

		return self.new_keyboard(*commands)

	@abc.abstractmethod
	def remove_keyboard(self):
		pass

	@abc.abstractmethod
	def real_send_text(self, user_model, text, keyboard=None):
		raise NotImplemented

	@abc.abstractmethod
	def real_send_photo(self, user_model, file_model, caption=None, keyboard=None):
		raise NotImplemented

	@abc.abstractmethod
	def real_send_video(self, user_model, file_model, caption=None, keyboard=None, duration=None):
		raise NotImplemented

	@abc.abstractmethod
	def real_send_video_note(self, user_model, file_model, caption=None, duration=None, length=None, keyboard=None):
		raise NotImplemented

	@abc.abstractmethod
	def real_send_voice(self, user_model, file_model, caption=None, duration=None, keyboard=None):
		raise NotImplemented

	@abc.abstractmethod
	def real_send_audio(self, user_model, file_model, caption=None, keyboard=None, duration=None, performer=None,
						title=None):
		raise NotImplemented

	@abc.abstractmethod
	def real_send_document(self, user_model, file_model, caption=None, keyboard=None):
		raise NotImplemented

	def send_audio(self, user_model, file_model, caption=None, keyboard=None, duration=None, performer=None,
				   title=None):

		sender = self
		if self.Type != user_model.chat_type:
			sender = self._get_sender(user_model.chat_type)

		if not keyboard:
			keyboard = sender._select_keyboard(user_model)

		sender.real_send_audio(user_model, file_model, caption=caption, keyboard=keyboard, duration=duration,
							   performer=performer, title=title)

	def send_voice(self, user_model, file_model, caption, keyboard=None):
		sender = self
		if self.Type != user_model.chat_type:
			sender = self._get_sender(user_model.chat_type)

		if not keyboard:
			keyboard = sender._select_keyboard(user_model)

		sender.real_send_voice(user_model, file_model, caption=caption, duration=None, keyboard=keyboard)

	def send_video_note(self, user_model, file_model, caption=None, keyboard=None):
		sender = self
		if self.Type != user_model.chat_type:
			sender = self._get_sender(user_model.chat_type)

		if not keyboard:
			keyboard = sender._select_keyboard(user_model)

		sender.real_send_video_note(user_model, file_model, caption=caption, duration=None, length=None,
									keyboard=keyboard)

	def send_video(self, user_model, file_model, caption=None, keyboard=None):
		sender = self
		if self.Type != user_model.chat_type:
			sender = self._get_sender(user_model.chat_type)

		if not keyboard:
			keyboard = sender._select_keyboard(user_model)

		sender.real_send_video(user_model, file_model, caption=caption, keyboard=keyboard, duration=None)

	def send_photo(self, user_model, file_model, caption=None, keyboard=None):

		sender = self
		if self.Type != user_model.chat_type:
			sender = self._get_sender(user_model.chat_type)

		if not keyboard:
			keyboard = sender._select_keyboard(user_model)

		sender.real_send_photo(user_model, file_model, caption=caption, keyboard=keyboard)

	def send_document(self, user_model, file_model, caption=None, keyboard=None):
		sender = self
		if self.Type != user_model.chat_type:
			sender = self._get_sender(user_model.chat_type)

		if not keyboard:
			keyboard = sender._select_keyboard(user_model)

		sender.real_send_document(user_model, file_model, caption=caption, keyboard=keyboard)

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

		sender.real_send_text(user_model, text, keyboard=keyboard)

	@abc.abstractmethod
	def registry_commands(self):
		pass

	def generic_command(self, message):

		user = self._get_user_from_message(message)

		if not user:
			self.welcome_command(message)
			return

		text_message = self.get_text_from_message(message)
		if text_message and len(text_message) and text_message[0] == '/':
			command = text_message[1:]

			# annullo l'ultimo comando..
			user.next_function = None
			user.save()

			getattr(self, command + '_command')(message)
			return

		if user.next_function:
			try:
				next_f = user.next_function
				user.next_function = None
				user.save()
				getattr(self, next_f)(message)
				return
			except Exception as e:
				logging.exception(e)
				self._registry_handler(user, user.next_function)
				return

		if not user.chat_with:
			# self.send_text(user_id, 'conversation_stopped_by_other_geostranger', language=language)
			return

		m = MessageModel(user=user)

		if text_message:
			m.text = text_message
			m.save()

			self.send_text(user.chat_with, text_message)

		caption_message = self.get_caption_from_message(message)

		image_url = self.get_image_url_from_message(message)
		if image_url:
			file_model = self._save_file(image_url, 'image/png')
			self.send_photo(user.chat_with, file_model, caption=caption_message)

		video_url = self.get_video_url_from_message(message)
		if video_url:
			file_model = self._save_file(video_url, 'video/mp4')
			self.send_video(user.chat_with, file_model, caption=caption_message)

		document_url = self.get_document_url_from_message(message)
		if document_url:
			file_model = self._save_file(document_url, '')
			self.send_document(user.chat_with, file_model, caption=caption_message)

		audio_url = self.get_audio_url_from_message(message)
		if audio_url:
			file_model = self._save_file(audio_url, 'audio/mp3')
			self.send_audio(user.chat_with, file_model, caption=caption_message, duration=None, performer=None,
							title=None)

	def welcome_command(self, message):

		user = self._get_user_from_message(message)

		if not user:
			user_id = self.get_user_id_from_message(message)
			language = self.get_user_language_from_message(message)

			user = UserModel(chat_type=str(self.Type), user_id=str(user_id), language=language)
			user.save()
			self.send_text(user, 'welcome')

		if not user.location:
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

	def search_command(self, message):

		# Devo effettuare una ricerca di un gruppo con limite 100.
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

		# L'utente fa il search. Posso utilizzarlo solamente se l'utente non è al momento sotto altra conversation.
		# Questo vuol dire che non devo fare nessun ciclo. E' UNA FUNZIONE ONE SHOT!
		# E se non trovo nulla, devo aspettare che sia un altro a fare questa operazione e "Trovarmi"..
		#

		# TODO URGENTE: Questa query seleziona tutti gli Utenti e non solamente quello più vicino.
		# http://docs.mongoengine.org/guide/querying.html#further-aggregation
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
		""" Devo effettuare atomicamente qua!! """

		actual_user = UserModel.objects(id=actual_user.id, chat_with=None).modify(chat_with=user_found, new=True)

		if actual_user.chat_with != user_found:
			""" Se sono già stato scelto durante questa query, allora semplicemente effettuo il release del utente.  """

			user_found.chat_with = None
			user_found.save()
			return

		au_tx = 'found_new_geostranger_first_time' if actual_user.first_time_chat else 'found_new_geostranger'

		# todo: Devo eliminare il messaggio "search.." messaggio o modificarlo!
		self.send_text(actual_user, au_tx,
					   format_with={'location_text': user_found.location_text})

		if actual_user.first_time_chat:
			actual_user.first_time_chat = False
			actual_user.save()

		"""Invia il messaggio al utente selezionato """

		uf_tx = 'found_new_geostranger_first_time' if user_found.first_time_chat else 'found_new_geostranger'

		self.send_text(user_found, uf_tx, format_with={'location_text': actual_user.location_text})

		if user_found.first_time_chat:
			user_found.first_time_chat = False
			user_found.save()

	def _handle_stop_step1(self, message):
		user = self._get_user_from_message(message)

		if not self._check_response(message, 'yes'):
			# TODO: edita il messaggio!
			self.send_text(user, 'not_stopped')
			return

		if user.chat_with:
			self.send_text(user.chat_with, 'conversation_stopped_by_other_geostranger')

			user.chat_with.chat_with = None
			user.chat_with.save()

		user.chat_with = None
		user.allow_search = False
		user.save()

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

		# TODO: qua posso modificare il testo, non inviarlo uno nuovo..

		self.send_text(user, 'location_saved', format_with={'location_text': user.location_text})

		""" Location ok! """

		if not user.completed:
			# send_to_user(telegram, message.from_user.id, language, 'ask_age', handler=handler_age_step)
			user.completed = True
			user.save()
			self.send_text(user, 'completed')

	def not_compatible(self, message):
		user = self._get_user_from_message(message)
		self.send_text(user, 'not_compatible')

	@abc.abstractmethod
	def process(self, request):
		raise NotImplemented
