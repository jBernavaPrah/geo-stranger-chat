from kik import KikApi, Configuration

import config
from kik_test_bot import CustomHandler


class CustomHandler(CustomHandler):
	Type = __name__
	_service = KikApi(config.KIK_BOT_USERNAME, config.KIK_BOT_KEY)

	def configuration(self):
		self._service.set_configuration(
			Configuration(webhook='https://%s%s' % (config.SERVER_NAME, config.KIK_BOT_WEBHOOK)))
