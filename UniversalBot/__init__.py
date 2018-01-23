# coding=utf-8

import logging

import datetime
from geopy import Nominatim
from mongoengine import Q

from controllers.resources.languages import trans_message
from models import UserModel, MessageModel
import abc


class Helper(object):
	__metaclass__ = abc.ABCMeta

	@staticmethod
	def _registry_handler(type_chat, user_id, handler_name):
		""" Salvo un handler per l'utente. Potrò gestire le risposte direttamente nel software.
			message_id: mi serve per poter modificare il messaggio e non inviare uno nuovo ogni volta.
		"""
		if hasattr(handler_name, '__name__'):
			handler_name = handler_name.__name__

		UserModel.objects(chat_type=str(type_chat), user_id=str(user_id), deleted_at=None) \
			.modify(next_function=handler_name, upsert=True)

	@staticmethod
	def _get_user(type_chat, user_id, strict=True):
		user = UserModel.objects(Q(chat_type=str(type_chat)) & \
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
		mod = __import__(sender_class)
		return getattr(mod, 'CustomHandler')()

	@abc.abstractmethod
	def get_user_id_from_message(self, message):
		return 0

	@abc.abstractmethod
	def get_user_language_from_message(self, message):
		return ''

	@abc.abstractmethod
	def get_photo_from_message(self, message):
		return ''

	@abc.abstractmethod
	def get_video_from_message(self, message):
		return ''

	@abc.abstractmethod
	def get_video_note_from_message(self, message):
		return ''

	@abc.abstractmethod
	def get_audio_from_message(self, message):
		return ''

	@abc.abstractmethod
	def get_voice_from_message(self, message):
		return ''

	@abc.abstractmethod
	def get_document_from_message(self, message):
		return ''

	@abc.abstractmethod
	def get_text_from_message(self, message):
		return ''

	@abc.abstractmethod
	def get_caption_from_message(self, message):
		return ''

	@abc.abstractmethod
	def get_data(self, message):
		return ''


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

	@abc.abstractmethod
	def remove_keyboard(self):
		pass

	@abc.abstractmethod
	def real_send_text(self, user_id, text, keyboard=None):
		raise NotImplemented

	@abc.abstractmethod
	def real_send_photo(self, user_id, photo, caption=None, keyboard=None):
		raise NotImplemented

	@abc.abstractmethod
	def real_send_video(self, user_id, video_file, caption=None, keyboard=None, duration=None):
		raise NotImplemented

	@abc.abstractmethod
	def real_send_video_note(self, user_id, video_note_file, caption=None, duration=None, length=None, keyboard=None):
		raise NotImplemented

	@abc.abstractmethod
	def real_send_voice(self, user_id, voice_file, caption=None, duration=None, keyboard=None):
		raise NotImplemented

	@abc.abstractmethod
	def real_send_audio(self, user_id, audio, caption=None, keyboard=None, duration=None, performer=None, title=None):
		raise NotImplemented

	@abc.abstractmethod
	def real_send_document(self, user_id, document_file, caption=None, keyboard=None):
		raise NotImplemented

	def send_audio(self, user_id, audio, caption=None, keyboard=None, duration=None, performer=None, title=None,
				   use=None):
		if not keyboard:
			keyboard = self.remove_keyboard()

		sender = self
		if use and self.Type != use:
			sender = self._get_sender(use)

		sender.real_send_audio(user_id, audio, caption=caption, keyboard=keyboard, duration=duration,
							   performer=performer, title=title)

	def send_voice(self, user_id, voice_file, caption, keyboard=None, use=None, ):
		if not keyboard:
			keyboard = self.remove_keyboard()

		sender = self
		if use and self.Type != use:
			sender = self._get_sender(use)

		sender.real_send_voice(user_id, voice_file, caption=caption, duration=None, keyboard=keyboard)

	def send_video_note(self, user_id, video_note_file, caption=None, keyboard=None, use=None):
		if not keyboard:
			keyboard = self.remove_keyboard()

		sender = self
		if use and self.Type != use:
			sender = self._get_sender(use)

		sender.real_send_video_note(user_id, video_note_file, caption=caption, duration=None, length=None,
									keyboard=keyboard)

	def send_video(self, user_id, video_file, caption=None, keyboard=None, use=None):
		if not keyboard:
			keyboard = self.remove_keyboard()

		sender = self
		if use and self.Type != use:
			sender = self._get_sender(use)

		sender.real_send_video(user_id, video_file, caption=caption, keyboard=keyboard, duration=None)

	def send_photo(self, user_id, photo_file, caption=None, keyboard=None, use=None):

		if not keyboard:
			keyboard = self.remove_keyboard()

		sender = self
		if use and self.Type != use:
			sender = self._get_sender(use)

		sender.real_send_photo(user_id, photo_file, caption=caption, keyboard=keyboard)

	def send_text(self, user_id, text, format_with=None, language=None, keyboard=None, use=None):

		if language:
			text = trans_message(language, text)

		if format_with:
			text = text.format(**format_with)

		if not keyboard:
			keyboard = self.remove_keyboard()

		sender = self
		if use and self.Type != use:
			sender = self._get_sender(use)

		sender.real_send_text(user_id, text, keyboard=keyboard)

	def send_document(self, user_id, document_file, caption=None, keyboard=None, use=None):
		if not keyboard:
			keyboard = self.remove_keyboard()

		sender = self
		if use and self.Type != use:
			sender = self._get_sender(use)

		sender.real_send_document(user_id, document_file, caption=caption, keyboard=keyboard)

	@abc.abstractmethod
	def registry_commands(self):

		pass

	def generic_command(self, message):
		user_id = self.get_user_id_from_message(message)

		user = self._get_user(self.Type, user_id, False)

		if not user or (not user.chat_with and not user.next_function):
			self.welcome_command(message)
			return

		if user.next_function:
			try:
				next_f = user.next_function
				return getattr(self, next_f)(user, message)
			except Exception as e:
				logging.exception(e)
				self._registry_handler(self.Type, user_id, user.next_function)
				return

		if not user.chat_with:
			# self.send_text(user_id, 'conversation_stopped_by_other_geostranger', language=language)
			return

		text_message = self.get_text_from_message(message)

		m = MessageModel(user=user)

		if text_message:
			m.text = text_message
			m.save()

			self.send_text(user.chat_with.user_id, '*GeoStranger:* ' + text_message, use=user.chat_with.chat_type)

		caption_message = self.get_caption_from_message(message)
		caption_message = "GeoStranger" + ': ' + caption_message if caption_message else ''

		photo_file = self.get_photo_from_message(message)
		if photo_file:
			m.photo.put(photo_file)
			m.save()
			# TODO: add other information of file here!
			self.send_photo(user_id, photo_file, caption_message, use=user.chat_with.chat_type)

		video_file = self.get_video_from_message(message)
		if video_file:
			m.video.put(video_file)
			m.save()
			# TODO: add other information of file here!
			self.send_video(user_id, video_file, caption=caption_message, use=user.chat_with.chat_type)

		video_note_file = self.get_video_note_from_message(message)
		if video_note_file:
			m.video_note.put(video_note_file)
			m.save()
			# TODO: add other information of file here!
			self.send_video_note(user_id, video_note_file, caption=caption_message, use=user.chat_with.chat_type)

		voice_file = self.get_voice_from_message(message)
		if voice_file:
			m.video_note.put(voice_file)
			m.save()
			# TODO: add other information of file here!
			self.send_voice(user_id, voice_file, caption=caption_message, use=user.chat_with.chat_type)

		document_file = self.get_document_from_message(message)
		if document_file:
			m.document.put(document_file)
			m.save()
			# TODO: add other information of file here!
			self.send_document(user_id, document_file, caption=caption_message, use=user.chat_with.chat_type)

		photo_file = self.get_photo_from_message(message)
		if photo_file:
			m.photo.put(photo_file)
			m.save()
			self.send_photo(user_id, photo_file, caption=caption_message, use=user.chat_with.chat_type)

	def welcome_command(self, message):
		user_id = self.get_user_id_from_message(message)
		language = self.get_user_language_from_message(message)

		user = self._get_user(self.Type, user_id, False)

		if not user:
			user = UserModel(chat_type=str(self.Type), user_id=str(user_id), language=language)
			user.save()
			self.send_text(user_id, 'welcome', language=language)

		if not user.location:
			self.location_command(message)
			return

		"""User is completed, need a search or change the location?"""
		self.send_text(user_id, 'search', language=language)

	def location_command(self, message):
		user_id = self.get_user_id_from_message(message)
		language = self.get_user_language_from_message(message)

		self.send_text(user_id, 'ask_location', language=language)
		self._registry_handler(self.Type, user_id, self._handler_location_step1)

	def delete_command(self, message):
		user_id = self.get_user_id_from_message(message)
		language = self.get_user_language_from_message(message)

		self.send_text(user_id, 'ask_delete_sure', language=language,
					   keyboard=self.new_keyboard(trans_message(language, 'yes'),
												  trans_message(language, 'no')))
		self._registry_handler(self.Type, user_id, self._handle_delete_step1)

	def terms_command(self, message):
		user_id = self.get_user_id_from_message(message)
		language = self.get_user_language_from_message(message)
		self.send_text(user_id, 'terms', language=language)

	def help_command(self, message):
		user_id = self.get_user_id_from_message(message)
		language = self.get_user_language_from_message(message)

		help_text = ''
		help_text += trans_message(language, 'command_start') + "\n"
		help_text += trans_message(language, 'command_stop') + "\n"
		help_text += trans_message(language, 'command_delete') + "\n"
		help_text += trans_message(language, 'command_terms') + "\n"
		help_text += trans_message(language, 'command_notify') + "\n"
		help_text += trans_message(language, 'command_help') + "\n"

		self.send_text(user_id, 'help', language=language,
					   format_with={'help_text': help_text})

	def stop_command(self, message):

		user_id = self.get_user_id_from_message(message)
		language = self.get_user_language_from_message(message)

		user = self._get_user(self.Type, user_id)

		if user.chat_with:

			self.send_text(user_id, 'ask_stop_also_current_chat', language=language,
						   keyboard=self.new_keyboard(trans_message(language, 'yes'),
													  trans_message(language, 'no')))
			self._registry_handler(self.Type, user_id, self._handle_stop_step1)

		else:
			self.send_text(user_id, 'ask_stop_sure', language=language,
						   keyboard=self.new_keyboard(trans_message(language, 'yes'),
													  trans_message(language, 'no')))
			self._registry_handler(self.Type, user_id, self._handle_stop_step1)

	def search_command(self, message):

		user_id = self.get_user_id_from_message(message)
		language = self.get_user_language_from_message(message)
		actual_user = self._get_user(self.Type, user_id)

		# controlla se l'utente non è in coversazione, altrimenti esegui il command_stop.
		if actual_user.chat_with:
			self.stop_command(message)
			return
		"""Per evitare di scrivere troppe volte in db"""
		if not actual_user.allow_search:
			actual_user.allow_search = True
			actual_user.save()

		# todo: Devo eliminare questo messaggio o modificarlo!
		self.send_text(user_id, 'in_search', language=language)

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

		# todo: Devo eliminare il messaggio "search.." messaggio o modificarlo!
		self.send_text(user_id, au_tx, language=language,
					   format_with={'location_text': user_found.location_text})

		if actual_user.first_time_chat:
			actual_user.first_time_chat = False
			actual_user.save()

		"""Invia il messaggio al utente selezionato """

		uf_tx = 'found_new_geostranger_first_time' if user_found.first_time_chat else 'found_new_geostranger'

		# TODO: Send it to correct chat type!
		self.send_text(user_id, uf_tx, language=language,
					   format_with={'location_text': actual_user.location_text})

		if user_found.first_time_chat:
			user_found.first_time_chat = False
			user_found.save()

	def _handle_stop_step1(self, user, message):
		user_id = self.get_user_id_from_message(message)
		language = self.get_user_language_from_message(message)

		if not self._check_response(message, 'yes'):
			# TODO: edita il messaggio!
			self.send_text(user_id, 'not_stopped', language=language)
			return

		if user.chat_with:
			self.send_text(user_id, 'conversation_stopped_by_other_geostranger', language=language)

			user.chat_with.chat_with = None
			user.chat_with.save()

		user.chat_with = None
		user.allow_search = False
		user.save()

		# TODO: edita il messaggio!
		self.send_text(user_id, 'stop', language=language)

	def _handle_delete_step1(self, user, message):

		user_id = self.get_user_id_from_message(message)
		language = self.get_user_language_from_message(message)

		if not self._check_response(message, 'yes'):
			self.send_text(user_id, 'not_deleted', language=language)
			return

		user.deleted_at = datetime.datetime.utcnow()
		user.save()
		self.send_text(user_id, 'delete_completed', language=language)

	def _handler_location_step1(self, user, message):

		user_id = self.get_user_id_from_message(message)
		language = self.get_user_language_from_message(message)
		location_text = self.get_text_from_message(message)

		if not location_text:
			self.send_text(user_id, 'location_error', language=language)
			self._registry_handler(self.Type, user_id, self._handler_location_step1)
			return

		geolocator = Nominatim()
		location = geolocator.geocode(location_text, language=language)

		if not location:
			""" Location non trovata.. """
			self.send_text(user_id, 'location_not_found', language=language,
						   format_with={'location_text': location_text})
			self._registry_handler(self.Type, user_id, self._handler_location_step1)
			return

		""" Location trovata! Per il momento la salvo e chiedo se è corretta :) """
		user.location = [location.longitude, location.latitude]
		user.location_text = location.address
		user.save()

		yes_no_keyboard = self.new_keyboard(trans_message(language, 'yes'), trans_message(language, 'no'))

		# TODO: qua posso modificare il testo, non inviarlo uno nuovo..

		self.send_text(user_id, 'ask_location_is_correct', language=language,
					   format_with={'location_text': location.address},
					   keyboard=yes_no_keyboard)
		self._registry_handler(self.Type, user_id, self._handler_location_step2)

	def _handler_location_step2(self, user, message):

		user_id = self.get_user_id_from_message(message)
		language = self.get_user_language_from_message(message)

		if not self._check_response(message, 'yes'):
			""" Richiedo allora nuovamente la posizione """
			self.send_text(user_id, 're_ask_location', language=language)
			self._registry_handler(self.Type, user_id, self._handler_location_step1)
			return

		# TODO: qua posso modificare il testo, non inviarlo uno nuovo..

		self.send_text(user_id, 'location_saved', format_with={'location_text': user.location_text},
					   language=language)

		""" Location ok! """
		# send_to_user(telegram, message.from_user.id, language, 'ask_age', handler=handler_age_step)
		user.completed = True
		user.save()
		self.send_text(user_id, 'completed', language=language)

	def not_compatible(self, message):
		pass

	@abc.abstractmethod
	def process(self, json_data):
		raise NotImplemented
