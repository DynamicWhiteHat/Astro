import openmeteo_requests
import requests_cache
from retry_requests import retry
from geopy.geocoders import Nominatim
from core.voice import speaker

cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

def get_weather(location, ui):
    geolocator = Nominatim(user_agent="geoapi")
    textLoc = geolocator.reverse((location.latitude, location.longitude), language='en', exactly_one=True)
    address = textLoc.raw.get('address', {})
    
    weather_descriptions = {
        0: "clear skies", 1: "mainly clear skies", 2: "partly cloudy skies", 3: "overcast conditions",
        45: "foggy conditions", 48: "depositing rime fog", 51: "light drizzle", 53: "moderate drizzle",
        55: "dense drizzle", 56: "light freezing drizzle", 57: "dense freezing drizzle", 61: "slight rain",
        63: "moderate rain", 65: "heavy rain", 66: "light freezing rain", 67: "heavy freezing rain",
        71: "slight snowfall", 73: "moderate snowfall", 75: "heavy snowfall", 77: "snow grains",
        80: "light rain showers", 81: "moderate rain showers", 82: "violent rain showers",
        85: "slight snow showers", 86: "heavy snow showers", 95: "thunderstorm",
        96: "thunderstorm with slight hail", 99: "thunderstorm with heavy hail"
    }

    params = {
        "latitude": location.latitude,
        "longitude": location.longitude,
        "daily": ["temperature_2m_max", "temperature_2m_min", "weather_code"],
        "current": ["temperature_2m", "weather_code"],
        "wind_speed_unit": "mph",
        "temperature_unit": "fahrenheit",
        "precipitation_unit": "inch"
    }

    responses = openmeteo.weather_api("https://api.open-meteo.com/v1/forecast", params=params)
    response = responses[0]

    current = response.Current()
    current_temperature_2m = current.Variables(0).Value()
    current_weather_code = current.Variables(1).Value()

    daily = response.Daily()
    daily_temperature_2m_max = daily.Variables(0).ValuesAsNumpy()
    daily_temperature_2m_min = daily.Variables(1).ValuesAsNumpy()
    daily_weather_code = daily.Variables(2).ValuesAsNumpy()

    weather_desc = weather_descriptions.get(current_weather_code, "unknown weather")
    daily_weather_desc = weather_descriptions.get(daily_weather_code[0], "unknown weather")

    message = f"Currently, in {address.get('county', '')}, {address.get('state', '')} it is {round(current_temperature_2m, 1)}° fahrenheit with {weather_desc}. Today, you can expect a high of {round(float(daily_temperature_2m_max[0]), 1)}° and a low of {round(float(daily_temperature_2m_min[0]), 1)}° with {daily_weather_desc}."
    print(message)
    ui.showResponseTextSignal.emit(message)
    speaker.yap(message)
