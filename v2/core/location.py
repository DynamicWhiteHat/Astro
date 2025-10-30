# Location Services
import geocoder
from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="geoapi")

class GeoLocation:
    def __init__(self, latlng):
        if latlng:
            self.latitude = latlng[0]
            self.longitude = latlng[1]
        else:
            self.latitude = None
            self.longitude = None

def get_location():
    g = geocoder.ip('me')
    if g.latlng:
        return GeoLocation(g.latlng)
    return None
