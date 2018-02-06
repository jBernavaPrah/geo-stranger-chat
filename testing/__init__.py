import json

from UniversalBot.languages import en

lang = {}

for k in dir(en):
	if not str(k).startswith('_'):
		lang[k] = getattr(en, k)

print(json.dumps(lang))
