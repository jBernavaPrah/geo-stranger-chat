# -*- coding: utf-8 -*-
import config
from UniversalBot.webchat_bot import CustomHandler
from UniversalBot.BotFrameworkMicrosoft import BotFrameworkMicrosoft, Skype


class CustomHandler(CustomHandler):
	Type = __name__
	_service = BotFrameworkMicrosoft(Skype(config.MICROSOFT_BOT_ID, config.MICROSOFT_BOT_KEY))
