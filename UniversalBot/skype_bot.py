import config
from UniversalBot.BotFrameworkMicrosoft import BotFrameworkMicrosoft, Skype as _Skype
from UniversalBot.webchat_bot import WebChat

skype_service = BotFrameworkMicrosoft(_Skype(config.MICROSOFT_BOT_ID, config.MICROSOFT_BOT_KEY))


class Skype(WebChat):
	_service = skype_service
