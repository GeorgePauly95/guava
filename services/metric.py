import asyncio
from typing import List
import json
from db import Workouts, Locations
from utils import calculate_time
from haversine import haversine
from db import Workouts, PauseAndResumeLogs, get_metrics


async def update_metrics(connection_manager):
    while True:
        await asyncio.sleep(5)
        try:
            active_connections = connection_manager.active_connections
            users = list(active_connections.keys())
            print("users", users, "\nactive connections", active_connections)
            metrics = get_metrics(users)
            print("metrics", metrics)
            # for user_id, websocket in connection_manager.active_connections.items():
            #     workout_id = Workouts.get_active_workouts_for_user(user_id)
            #     if workout_id is None:
            #         continue
            #     metrics = await get_metrics(workout_id)
            #     if metrics is None:
            #         continue
            #     await websocket.send_text(json.dumps(metrics))
        except Exception as e:
            print("Error: ", e)
