
import config
from UniversalBot.SkypeBot import SkypeBot
from skype_test_bot import CustomHandler


class CustomHandler(CustomHandler):
	Type = __name__
	_service = SkypeBot(config.SKYPE_BOT_KEY)

