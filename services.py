from haversine import haversine
from models import Locations, Workouts, PauseAndResumeLogs
import json
import asyncio
from datetime import datetime


def handle_status(workout_id, status, time):
    if status == "stop":
        Workouts.stop_workout(workout_id, time)
    elif status == "pause":
        PauseAndResumeLogs.pause_workout(workout_id, time)
    else:
        PauseAndResumeLogs.resume_workout(workout_id, time)


def validate_location(location, workout_id):
    workout = Workouts.get_workout(workout_id)

    if datetime.fromisoformat(location["time"]) < workout["started_at"]:
        return False
    elif datetime.fromisoformat(location["time"]) > workout["stopped_at"]:
        return False
    return True


def store_location(location):
    workout_id = location["workout_id"]
    if validate_location(location, workout_id):
        Locations.store_location(location)


def handle_message(message):
    if message["type"] == "location":
        store_location(message["payload"])


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


async def get_metrics(workout_id: int):
    locations = Locations.get_workout_locations(workout_id)
    return calculate_metrics(locations)


def calculate_metrics(locations):
    distance = calculate_distance(locations)
    time = calculate_time(locations)
    return {"distance": distance, "time": time}


async def update_metrics(websocket):
    while True:
        await asyncio.sleep(5)
        workout_id = Workouts.get_active_workout()
        if workout_id is not None:
            metrics = await get_metrics(workout_id)
            await websocket.send_text(json.dumps(metrics))
