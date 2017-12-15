import geocoder



g = geocoder.geonames('Eraclea Ve', maxRows=5)
for result in g:
	print result