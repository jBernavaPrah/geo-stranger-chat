# coding=utf-8
import telebot
import time

import config
from UniversalBot import trans_message

telegram = telebot.TeleBot(config.STRANGERGEO_KEY, threaded=False)
telegram.chat_type = __name__
telegram.set_webhook(url='https://%s%s' % (config.SERVER_NAME, config.WEBHOOK_STRANGERGEO))


@telegram.message_handler(func=lambda message: True)
def echo_all(message):
	text = trans_message(message.from_user.language_code, 'go_to_real_geostranger_account')

	telegram.reply_to(message, text)

	return

# msg = strangergeo.send_message(message.chat.id, message.text)
# time.sleep(3)

# strangergeo.delete_message(message.chat.id, msg.message_id)
# strangergeo.edit_message_text('nuovo testo', msg.chat.id, msg.message_id)

# pass

# send_to_user(strangergeo, '536888144', 'it', message.text)
# strangergeo.forward_message('536888144', message.chat.id, message.message_id)

# reply_to_message(strangergeo, message, 'go_to_real_geostranger_account')
