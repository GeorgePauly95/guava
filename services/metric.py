import asyncio
import json
from models import Workouts, Locations
from utils import calculate_time
from haversine import haversine


def calculate_distance(locations):
    distances = [
        haversine(
            (locations[i]["latitude"], locations[i]["longitude"]),
            (locations[i + 1]["latitude"], locations[i + 1]["longitude"]),
        )
        for i in range(len(locations) - 1)
    ]
    return sum(distances)


def calculate_metrics(locations):
    distance = calculate_distance(locations)
    time = calculate_time(locations)
    return {"distance": distance, "time": time}


def validate_locations(locations, workout_id):
    logs = PauseAndResumeLogs.get_logs(workout_id)
    if logs == []:
        return locations

    def validate_location(location):
        nonlocal logs
        for log in logs:
            if log["resumed_at"] is None:
                if location["time"] > log["paused_at"]:
                    return False
            else:
                if (
                    location["time"] > log["paused_at"]
                    and location["time"] < log["resumed_at"]
                ):
                    return False
        return True

    validated_locations = list(filter(validate_location, locations))
    return validated_locations


async def get_metrics(workout_id: int):
    locations = Locations.get_workout_locations(workout_id)
    if len(locations) < 2:
        return None
    validated_locations = validate_locations(locations, workout_id)
    return calculate_metrics(validated_locations)


async def update_metrics(websocket):
    while True:
        await asyncio.sleep(5)
        workout_ids = Workouts.get_active_workouts()
        if workout_ids is not None:
            for workout_id in workout_ids:
                metrics = await get_metrics(workout_id)
                if metrics is not None:
                    await websocket.send_text(json.dumps(metrics))
                print(f"Workout with id: {workout_id} has no location datapoints yet.")
