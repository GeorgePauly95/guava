from haversine import haversine
from models import Locations, Workouts, PauseAndResumeLogs
from schemas import WorkoutModifyResponse
import json
import asyncio
from datetime import datetime


def modify_workout(workout_id, status, time):
    workout = Workouts.get_workout(workout_id)
    if workout is None or workout["started_at"] > time:
        return WorkoutModifyResponse(
            success=False,
            error=f"Workout with id: {workout_id} doesn't exist.",
            status="WORKOUT_NOT_FOUND",
        )

    if workout["stopped_at"] is not None:
        return WorkoutModifyResponse(
            success=False,
            error=f"Workout with id: {workout_id} is already completed.",
            status="WORKOUT_ALREADY_COMPLETED",
        )

    if status == "stop":
        Workouts.stop_workout(workout_id, time)
        return WorkoutModifyResponse(success=True, status="WORKOUT_STOPPED")

    elif status == "pause":
        PauseAndResumeLogs.pause_workout(workout_id, time)
        return WorkoutModifyResponse(success=True, status="WORKOUT_PAUSED")
    else:
        PauseAndResumeLogs.resume_workout(workout_id, time)
        return WorkoutModifyResponse(success=True, status="WORKOUT_RESUMED")


def store_location(location):
    def validate_location(location, workout_id):
        workout = Workouts.get_workout(workout_id)

        if workout is None:
            return False
        elif datetime.fromisoformat(location["time"]) < workout["started_at"]:
            return False
        elif (
            workout["stopped_at"] is not None
            and datetime.fromisoformat(location["time"]) > workout["stopped_at"]
        ):
            return False
        return True

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


def validate_locations(locations, workout_id):
    logs = PauseAndResumeLogs.get_logs(workout_id)
    return locations


async def get_metrics(workout_id: int):
    locations = Locations.get_workout_locations(workout_id)
    if len(locations) < 2:
        return None
    validated_locations = validate_locations(locations, workout_id)
    return calculate_metrics(locations)


def calculate_metrics(locations):
    distance = calculate_distance(locations)
    time = calculate_time(locations)
    return {"distance": distance, "time": time}


async def update_metrics(websocket):
    while True:
        await asyncio.sleep(5)
        workout_ids = Workouts.get_active_workouts()
        if workout_ids is not None:
            for workout_id in workout_ids:
                metrics = await get_metrics(workout_id)
                await websocket.send_text(json.dumps(metrics))
