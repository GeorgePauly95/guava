import asyncio
import json
from db import Workouts, Locations
from utils import calculate_time
from haversine import haversine
from db import Workouts, PauseAndResumeLogs


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


async def update_metrics(connection_manager):
    while True:
        await asyncio.sleep(5)
        try:
            user_ids = list(connection_manager.active_connections.keys())
            active_workouts = Workouts.get_active_workouts_for_users(user_ids)
            active_connections = list(connection_manager.active_connections.items())
            print(
                "active_workouts:",
                active_workouts,
                "\nactive_connections:",
                active_connections,
            )
            for user_id, websocket in active_connections:
                for active_workout in active_workouts:
                    if active_workout["user_id"] == user_id:
                        workout_id = active_workout["id"]
                        if workout_id is None:
                            continue
                        metrics = await get_metrics(workout_id)
                        if metrics is None:
                            continue
                        await websocket.send_text(json.dumps(metrics))
                    else:
                        return
        except Exception as e:
            print("Error: ", e)


# async def update_metrics(connection_manager):
#     while True:
#         await asyncio.sleep(5)
#         print("active connections:", connection_manager.active_connections)
#         try:
#             for user_id, websocket in connection_manager.active_connections.items():
#                 workout_id = Workouts.get_active_workouts_for_user(user_id)
#                 if workout_id is None:
#                     continue
#                 metrics = await get_metrics(workout_id)
#                 if metrics is None:
#                     continue
#                 await websocket.send_text(json.dumps(metrics))
#         except Exception as e:
#             print("Error: ", e)
