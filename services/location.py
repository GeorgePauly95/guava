from datetime import datetime
from models import Locations, Workouts


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
