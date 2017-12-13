import utilities
from utilities import RedisList


class Location(utilities.RedisDict):
	'''A user. Duh.'''

	def __init__(self, id=None, **defaults):
		lat = defaults.get('latitude', None)
		lon = defaults.get('longitude', None)

		utilities.RedisDict.__init__(
			self,
			id=id or str(lat) + str(lon),
			fields={
				'latitude': str,
				'longitude': str,
				'city': str,
			},
			defaults=defaults
		)


class User(utilities.RedisDict):
	def __init__(self, id=None, **defaults):
		utilities.RedisDict.__init__(
			self,
			id=id,
			fields={
				'name': str,
				'age': int,
				'location': Location,
				'exists': bool,
				'chat': RedisList.as_child(self, 'friends', User),
			},
			defaults=defaults
		)


if __name__ == '__main__':
	luke = User(name='Luke Skywalker', age=34)

	pos = Location(latitude='123', longitude=456)

	luke['location'] = pos

	print(luke['location'])
	print(luke['name'])

	han = User(name='hans', age=34)
	luke['chat'].append(han)

	print(len(luke['chat']))
