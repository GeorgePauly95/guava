def status_code_map(status):
    if status == "WORKOUT_NOT_FOUND":
        return 404
    elif status in {
        "WORKOUT_ALREADY_COMPLETED",
        "WORKOUT_NOT_PAUSED",
        "WORKOUT_ALREADY_PAUSED",
    }:
        return 409
    elif status == "BAD_REQUEST":
        return 400
    return 200
