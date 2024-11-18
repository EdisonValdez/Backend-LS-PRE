# Connection to the Google direction's API
import requests
from django.conf import settings

base_url = "https://maps.googleapis.com/maps/api/directions/json?"


# Waypoints -> waypoints=49.2,48.7|36.12,43.21


def get_directions(origin, destination, waypoints, mode):
    origin_lat, origin_lon = origin[0], origin[1]
    destination_lat, destination_lon = destination[0], destination[1]
    waypoint_list = ""
    for waypoint in waypoints:
        waypoint_list += f"{waypoint[0]},{waypoint[1]}|"
    waypoint_list = waypoint_list[:-1]
    url = f"{base_url}origin={origin_lat},{origin_lon}&destination={destination_lat},{destination_lon}&waypoints={waypoint_list}&mode={mode}&key={settings.DIRECTIONS_API_KEY}"
    response = requests.get(url)
    return response.json()


