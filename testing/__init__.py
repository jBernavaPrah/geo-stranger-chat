from geopy import GoogleV3

import config

geolocator = GoogleV3(api_key=config.GOOGLE_API_KEY)
location = geolocator.geocode('Eraclea', language='it')

print(location)
