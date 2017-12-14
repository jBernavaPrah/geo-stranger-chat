# from utilities import rom
import rom


def cb(data):
	# ``data`` can act as an object or dictionary. This function could have
	# actually just read::
	#     return data
	# ... but we will be explicit in what we return... yes this works!
	return {'lon': data['lon'], 'lat': data.lat}


class PointOfInterest(rom.Model):
	tags = rom.String(index=True, keygen=rom.FULL_TEXT)
	avg_rating = rom.Float(index=True)
	lon = rom.Float()
	lat = rom.Float()
	geo_index = [
		# callback function passed to GeoIndex as the 2nd argument *must*
		# return a dictionary containing 'lon' and 'lat' values, as degrees
		rom.GeoIndex('geo_index', cb),
	]


if __name__ == '__main__':
	points = PointOfInterest.query \
		.filter(tags='restaurant') \
		.near('geo_index', '', '', 25, 'km') \
		.order_by('-avg_rating') \
		.limit(0, 50) \
		.all()

	print(points)
