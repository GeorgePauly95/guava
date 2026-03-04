from haversine import haversine
from models import Locations


async def get_metrics(workout_id: int):
    locations = Locations.get_workout_locations(workout_id)
    return calculate_metrics(locations)


def store_location(location):
    Locations.store_location(location)


def calculate_metrics(locations):
    distance = calculate_distance(locations)
    time = calculate_time(locations)
    return {"distance": distance, "time": time}


def calculate_distance(locations):
    distances = [
        haversine(
            (locations[i]["latitude"], locations[i]["longitude"]),
            (locations[i + 1]["latitude"], locations[i + 1]["longitude"]),
        )
        for i in range(len(locations) - 1)
    ]
    return sum(distances)


def calculate_time(locations):
    first_location = locations[0]
    latest_location = locations[-1]
    time = latest_location["time"] - first_location["time"]
    return str(time)
