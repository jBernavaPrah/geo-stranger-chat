from geopy import Nominatim

geolocator = Nominatim(user_agent='')
print(geolocator.reverse((43.1479, 12.1097)))
