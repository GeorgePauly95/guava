import json
import asyncio
from db import get_metrics


async def update_metrics(connection_manager):
    while True:
        await asyncio.sleep(5)
        try:
            active_connections = connection_manager.active_connections
            users = list(active_connections.keys())
            metrics = get_metrics(users)
            for metric in metrics:
                print("type", type(metric))
                user_id = metric.get("user_id")
                websocket = active_connections.get(user_id)
                await websocket.send_text(json.dumps(metric))
        except Exception as e:
            print("Error: ", e)
