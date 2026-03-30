def status_code_map(outcome_status):
    if outcome_status == "WORKOUT_NOT_FOUND":
        return 404
    elif outcome_status in {
        "WORKOUT_ALREADY_COMPLETED",
        "WORKOUT_NOT_PAUSED",
        "WORKOUT_ALREADY_PAUSED",
    }:
        return 409
    return 200


def calculate_time(locations):
    first_location = locations[0]
    latest_location = locations[-1]
    time = latest_location["time"] - first_location["time"]
    return str(time)
