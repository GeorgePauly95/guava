from haversine import haversine
from models import Locations, Workouts


async def get_metrics(workout_id: int):
    locations = Locations.get_workout_locations(workout_id)
    validated_locations = validate_locations(locations, workout_id)
    return calculate_metrics(validated_locations)


def store_location(location):
    Locations.store_location(location)


def validate_locations(locations, workout_id):
    workout = Workouts.get_workout(workout_id)
    validated_locations = [
        location
        for location in locations
        if location["created_at"] > workout["created_at"]
        and location["created_at"] > workout["stopped_at"]
    ]
    return validated_locations


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
