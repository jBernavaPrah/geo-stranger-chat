# coding=utf-8

import logging

from geopy import Nominatim
from mongoengine import Q

from controllers.resources.languages import trans_message
from models import UserModel
import abc


class Helper(object):
	__metaclass__ = abc.ABCMeta
	Type = __name__

	def _registry_handler(self, user_id, handler_name):
		""" Salvo un handler per l'utente. Potrò gestire le risposte direttamente nel software.
			message_id: mi serve per poter modificare il messaggio e non inviare uno nuovo ogni volta.
		"""
		if hasattr(handler_name, '__name__'):
			handler_name = handler_name.__name__

		UserModel.objects(chat_type=self.Type, user_id=str(user_id), deleted_at=None) \
			.modify(next_function=handler_name, upsert=True)

	def _get_user(self, user_id, strict=True):
		user = UserModel.objects(Q(chat_type=str(self.Type)) & \
								 Q(user_id=str(user_id)) & \
								 Q(deleted_at=None)) \
			.first()

		if not user and strict:
			logging.exception('User required, but not found.')
			raise RuntimeError

	@abc.abstractmethod
	def _get_user_id(self, message):
		pass

	@abc.abstractmethod
	def _get_user_language(self, message):
		pass

	@abc.abstractmethod
	def _get_text(self, message):
		pass

	@abc.abstractmethod
	def _yes_no_keyboard(self, yes_text, no_text):
		pass

	@abc.abstractmethod
	def _remove_keyboard(self):
		pass

	@abc.abstractmethod
	def _get_data(self, message):
		pass

	def _check_response(self, message, check, strict=False):

		language = self._get_user_language(message)
		m = self._get_data(message)
		if not m:
			m = self._get_text(message)

		if not m:
			return False

		w = trans_message(language, check)

		if not strict:
			return m.lower().strip() == w.lower().strip()

		return m == w


class Commands(object):
	__metaclass__ = abc.ABCMeta

	@abc.abstractmethod
	def welcome_command(self, message):
		pass

	@abc.abstractmethod
	def location_command(self, message):
		pass

	@abc.abstractmethod
	def delete_command(self, message):
		pass

	@abc.abstractmethod
	def help_command(self, message):
		pass

	@abc.abstractmethod
	def stop_command(self,message):
		pass

	@abc.abstractmethod
	def search_command(self,message):
		pass


class Handler(Helper, Commands):

	__metaclass__ = abc.ABCMeta

	def _on_welcome_message(self, message):

		user_id = self._get_user_id(message)
		language = self._get_user_language(message)

		user = self._get_user(user_id, False)

		if not user:
			user = UserModel(chat_type=self.Type, user_id=str(user_id),
							 language=language)
			user.save()
			self._send_text(user_id, 'welcome', language=language)

		if not user.location:
			self._on_location_change(message)
			return

		"""User is completed, need a search or change the location?"""
		self._send_text(user_id, language, 'search')

	def _on_location_change(self, message):
		user_id = self._get_user_id(message)
		language = self._get_user_language(message)

		self._send_text(user_id, 'ask_location', language=language)
		self._registry_handler(user_id, self._handler_location_step1)

	def _handler_location_step1(self, message):

		user_id = self._get_user_id(message)
		language = self._get_user_language(message)
		location_text = self._get_text(message)

		if not location_text:
			self._send_text(user_id, 'location_error', language=language)
			self._registry_handler(user_id, self._handler_location_step1)
			return

		geolocator = Nominatim()
		location = geolocator.geocode(location_text, language=message.from_user.language_code)

		if not location:
			""" Location non trovata.. """
			self._send_text(user_id, 'location_not_found', language=language,
							format_with={'location_text': location_text})
			self._registry_handler(user_id, self._handler_location_step1)
			return

		user = self._get_user(user_id)

		""" Location trovata! Per il momento la salvo e chiedo se è corretta :) """
		user.location = [location.longitude, location.latitude]
		user.location_text = location.address
		user.save()

		yes_no_keyboard = self._yes_no_keyboard(trans_message(language, 'yes'), trans_message(language, 'no'))

		# TODO: qua posso modificare il testo, non inviarlo uno nuovo..

		self._send_text(user_id, 'ask_location_is_correct', format_with={'location_text': location.address},
						keyboard=yes_no_keyboard)
		self._registry_handler(user_id, self._handler_location_step2)

	def _handler_location_step2(self, message):

		user_id = self._get_user_id(message)
		language = self._get_user_language(message)

		if not self._check_response(message, 'yes'):
			""" Richiedo allora nuovamente la posizione """
			self._send_text(user_id, 're_ask_location', language=language)
			self._registry_handler(user_id, self._handler_location_step1)
			return

		# TODO: qua posso modificare il testo, non inviarlo uno nuovo..

		user = self._get_user(user_id)
		self._send_text(user_id, 'location_saved', format_with={'location_text': user.location_text}, language=language)

		""" Location ok! """
		# send_to_user(telegram, message.from_user.id, message.from_user.language_code, 'ask_age', handler=handler_age_step)
		user.completed = True
		user.save()
		self._send_text(user_id, 'completed', language=language)

	def _handle_message(self, message):

		user_id = self._get_user_id(message)

		user = self._get_user(user_id, False)

		if not user or (not user.chat_with and not user.next_function):
			self._on_welcome_message(message)
			return

		if user.next_function:
			try:
				next_f = user.next_function
				return getattr(self, next_f)(message)
			except Exception as e:
				logging.exception(e)
				self._registry_handler(user_id, user.next_function)
				return

	def _send_text(self, user_id, text, format_with=None, language=None, keyboard=None):

		if language:
			text = trans_message(language, text)

		if format_with:
			text = text.format(**format_with)

		if not keyboard:
			keyboard = self._remove_keyboard()

		self.send_text(user_id, text, keyboard=keyboard)

	@abc.abstractmethod
	def send_text(self, user_id, text, keyboard=None):
		raise NotImplemented

	@abc.abstractmethod
	def send_photo(self, user_id, photo):
		raise NotImplemented

	@abc.abstractmethod
	def send_video(self, user_id, video):
		raise NotImplemented

	@abc.abstractmethod
	def send_audio(self, user_id, audio):
		raise NotImplemented

	@abc.abstractmethod
	def process(self,json_data):
		raise NotImplemented
