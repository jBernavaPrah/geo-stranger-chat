from UniversalBot.AbstractHandler import AppInfo
from UniversalBot.kik_bot import KIK
from UniversalBot.microsoft_bot import MicrosoftBot
from UniversalBot.telegram_bot import Telegram
from UniversalBot.telegram_bot_strangergeo import StrangerGeoTelegram
from UniversalBot.facebook_bot import FacebookBot


class AlloInfo(AppInfo):
	name = 'Google Allo'
	logo = 'img/bot/Google_Allo_Logo.png'


class SignalInfo(AppInfo):
	name = 'Signal'
	logo = 'img/bot/signal_logo.png'


class SlackInfo(AppInfo):
	name = 'Slack'
	logo = 'img/bot/slack_alt.png'


class LineInfo(AppInfo):
	name = 'Line'
	logo = 'img/bot/LINE_logo.png'


class DiscordInfo(AppInfo):
	name = 'Discord'
	logo = 'img/bot/Discord-logo.png'


class SnapchatInfo(AppInfo):
	name = 'Snapchat'
	logo = 'img/bot/snapchat_logo.png'


class VoxerInfo(AppInfo):
	name = 'Voxer'
	logo = 'img/bot/voxer-orange.png'


class KakaotalkInfo(AppInfo):
	name = 'Kakaotalk'
	logo = 'img/bot/kakaotalk-logo-yellow.png'
