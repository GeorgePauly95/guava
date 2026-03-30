import asyncio
import json
from datetime import datetime
from haversine import haversine
from utils import calculate_time
from models import Locations, PauseAndResumeLogs, Workouts


def check_log_conflict(log, time):
    if log["paused_at"] < time and log["resumed_at"] > time:
        return True
    return False


def pause_workout(workout_id, time):
    logs = PauseAndResumeLogs.get_logs(workout_id)
    active_sessions = [
        log
        for log in logs
        if log["resumed_at"] is None or check_log_conflict(log, time)
    ]
    if len(active_sessions) != 0:
        return {
            "success": False,
            "error_message": f"Workout with id: {workout_id} has already been paused.",
            "outcome_status": "WORKOUT_ALREADY_PAUSED",
        }
    PauseAndResumeLogs.pause_workout(workout_id, time)
    return {"success": True, "outcome_status": "WORKOUT_PAUSED"}


def resume_workout(workout_id, time):
    logs = PauseAndResumeLogs.get_logs(workout_id)
    valid_ids = [
        log["id"]
        for log in logs
        if log["resumed_at"] is None and time > log["paused_at"]
    ]
    if valid_ids == []:
        return {
            "success": False,
            "error_message": f"Workout with id: {workout_id} is not currently paused.",
            "outcome_status": "WORKOUT_NOT_PAUSED",
        }

    for id in valid_ids:
        PauseAndResumeLogs.resume_workout(id, time)
    return {"success": True, "outcome_status": "WORKOUT_RESUMED"}


def stop_workout(workout_id, workout, time):
    if workout["stopped_at"] is not None:
        return {
            "success": False,
            "error_message": f"Workout with id: {workout_id} has already been stopped.",
            "outcome_status": "WORKOUT_ALREADY_COMPLETED",
        }
    logs = PauseAndResumeLogs.get_logs(workout_id)
    for log in logs:
        if log["resumed_at"] is None and log["paused_at"] > time:
            return {
                "success": False,
                "error_message": f"Workout with id: {workout_id} cannot be stopped.",
                "outcome_status": "WORKOUT_NOT_STOPPED",
            }
        elif log["resumed_at"] is not None and log["resumed_at"] > time:
            return {
                "success": False,
                "error_message": f"Workout with id: {workout_id} cannot be stopped.",
                "outcome_status": "WORKOUT_NOT_STOPPED",
            }
    Workouts.stop_workout(workout_id, time)
    return {"success": True, "outcome_status": "WORKOUT_STOPPED"}


def route_modify_workout(workout_id, status, time):
    workout = Workouts.get_workout(workout_id)

    if workout is None or workout["started_at"] > time:
        return {
            "success": False,
            "error_message": f"Workout with id: {workout_id} doesn't exist.",
            "outcome_status": "WORKOUT_NOT_FOUND",
        }
    elif workout["stopped_at"] is not None and workout["stopped_at"] < time:
        return {
            "success": False,
            "error_message": f"Workout with id: {workout_id} is already stopped.",
            "outcome_status": "WORKOUT_ALREADY_COMPLETED",
        }
    elif status == "stop":
        return stop_workout(workout_id, workout, time)
    elif status == "pause":
        return pause_workout(workout_id, time)
    else:
        return resume_workout(workout_id, time)


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
                if metrics is not None:
                    await websocket.send_text(json.dumps(metrics))
                print(f"Workout with id: {workout_id} has no location datapoints yet.")
