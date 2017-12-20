from geopy.geocoders import Nominatim

geolocator = Nominatim()
location = geolocator.geocode("Eraclea",language='it')

print(location.address)
print((location.latitude, location.longitude))
