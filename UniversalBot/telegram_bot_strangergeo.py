from UniversalBot.telegram_bot import Telegram
from utilities import strangergeo_service


class StrangerGeoTelegram(Telegram):
	_service = strangergeo_service
