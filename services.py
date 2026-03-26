from haversine import haversine
from models import Locations, Workouts, PauseAndResumeLogs
import json
import asyncio
from datetime import datetime


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
    # use len function to check if the array is empty
    if active_sessions != []:
        return {
            "success": False,
            "error": f"Workout with id: {workout_id} has already been paused.",
            "status": "WORKOUT_ALREADY_PAUSED",
        }
    PauseAndResumeLogs.pause_workout(workout_id, time)
    return {"success": True, "status": "WORKOUT_PAUSED"}


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
            "error": f"Workout with id: {workout_id} is not currently paused.",
            "status": "WORKOUT_NOT_PAUSED",
        }

    for id in valid_ids:
        PauseAndResumeLogs.resume_workout(id, time)
    return {"success": True, "status": "WORKOUT_RESUMED"}


def stop_workout(workout_id, workout, time):
    if workout["stopped_at"] is not None:
        return {
            "success": False,
            "error": f"Workout with id: {workout_id} has already been stopped.",
            "status": "WORKOUT_ALREADY_COMPLETED",
        }
    logs = PauseAndResumeLogs.get_logs(workout_id)
    for log in logs:
        if log["resumed_at"] is None and log["paused_at"] > time:
            return {
                "success": False,
                "error": f"Workout with id: {workout_id} cannot be stopped.",
                "status": "BAD_REQUEST",
            }
        elif log["resumed_at"] is not None and log["resumed_at"] > time:
            return {
                "success": False,
                "error": f"Workout with id: {workout_id} cannot be stopped.",
                # error_message not error
                # outcome_status not status, and service layer should not know 'REQUEST'
                "status": "BAD_REQUEST",
            }
    Workouts.stop_workout(workout_id, time)
    return {"success": True, "status": "WORKOUT_STOPPED"}


def route_modify_workout(workout_id, status, time):
    workout = Workouts.get_workout(workout_id)

    if workout is None or workout["started_at"] > time:
        return {
            "success": False,
            "error": f"Workout with id: {workout_id} doesn't exist.",
            "status": "WORKOUT_NOT_FOUND",
        }
    elif workout["stopped_at"] is not None and workout["stopped_at"] < time:
        return {
            "success": False,
            "error": f"Workout with id: {workout_id} is already stopped.",
            "status": "BAD_REQUEST",
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


def calculate_time(locations):
    first_location = locations[0]
    latest_location = locations[-1]
    time = latest_location["time"] - first_location["time"]
    return str(time)


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
