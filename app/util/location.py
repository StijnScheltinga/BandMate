import math
from app.config import settings
import requests

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c

def get_city_from_latlong(lat, long):
    url = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={lat},{long}&key={settings.GOOGLE_MAPS_API_KEY}"
    response = requests.get(url).json()
    
    if response.get("status") == "OK" and response.get("results"):
        components = response["results"][0]["address_components"]

        # Priority order: locality > postal_town > administrative_area_level_2 > administrative_area_level_1
        preferred_types = [
            "locality",                        # city
            "administrative_area_level_2",     # municipality
            "administrative_area_level_1"      # province
        ]

        for t in preferred_types:
            for component in components:
                if t in component.get("types", []):
                    return component["long_name"]

    return None