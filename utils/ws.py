from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[int, WebSocket] = {}

    async def create_connection(self, user_id: int, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def remove_connection(self, user_id):
        self.active_connections.pop(user_id)


connection_manager = ConnectionManager()
