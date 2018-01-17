# coding=utf-8
import telebot
import time

import config
from controllers.resources.telegram_base import reply_to_message, send_to_user

strangergeo = telebot.TeleBot(config.STRANGERGEO_KEY, threaded=False)
strangergeo.chat_type = 'telegram'


@strangergeo.message_handler(func=lambda message: True,
							 content_types=['audio', 'video', 'document', 'text', 'location', 'contact', 'sticker'])
def echo_all(message):
	reply_to_message(strangergeo, message, 'go_to_real_geostranger_account')
	return

	#msg = strangergeo.send_message(message.chat.id, message.text)
	#time.sleep(3)

	# strangergeo.delete_message(message.chat.id, msg.message_id)
	#strangergeo.edit_message_text('nuovo testo', message.chat.id, message.message_id)

	#pass

# send_to_user(strangergeo, '536888144', 'it', message.text)
# strangergeo.forward_message('536888144', message.chat.id, message.message_id)

# reply_to_message(strangergeo, message, 'go_to_real_geostranger_account')
